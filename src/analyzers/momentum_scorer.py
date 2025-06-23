"""
Repository scoring module for the Early Stage GitHub Signals platform.
Implements the 10-point scoring system focused on momentum detection.
"""
import re
import datetime
from datetime import timezone, timedelta
from typing import Dict, List, Any, Tuple

import requests
from github import Github
from github.GithubException import RateLimitExceededException


class MomentumScorer:
    """
    Repository Momentum Scorer implementing the 10-point scoring system.
    """
    
    def __init__(self, config=None, github_client=None, logger=None):
        """
        Initialize the momentum scorer.
        
        Args:
            config: Configuration manager (optional)
            github_client: GitHub API client (optional)
            logger: Logger instance (optional)
        """
        self.config = config
        self.github = github_client
        self.logger = logger
        
        # Default to 14 days for commit and star velocity
        self.momentum_days = 14
        
        # Developer ecosystem languages and topics
        self.dev_languages = ["python", "typescript", "rust"]
        self.dev_topics = ["devops", "cli", "sdk", "api", "developer-tools"]
    
    def score_repository(self, repo_data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        """
        Score a repository based on the 10-point momentum system.
        
        Args:
            repo_data: Repository data
            
        Returns:
            Tuple of (score, details) where details explains the scoring
        """
        # Check if we have essential data
        if not repo_data.get('full_name'):
            if self.logger:
                self.logger.warning("Missing repository full_name in repo_data")
            
        if not self.github:
            if self.logger:
                self.logger.warning("GitHub client is not configured properly - scoring will be limited")
        
        score = 0
        details = {
            'commit_surge': 0,
            'star_velocity': 0,
            'team_traction': 0,
            'dev_ecosystem_fit': 0,
            'signals': []
        }
        
        # Get the GitHub repository object if we have a client
        repo_obj = None
        repo_metrics = {
            'stars': 0,
            'stars_gained_14d': 0,
            'forks': 0,
            'forks_gained_14d': 0,
            'commits_14d': 0,
            'contributors_30d': 0,
            'avg_issue_resolution_days': 30  # Default assumption
        }
        
        # Pre-populate metrics from repo_data if available (as fallback)
        if 'stars' in repo_data:
            repo_metrics['stars'] = repo_data.get('stars', 0)
        if 'recent_stars' in repo_data:
            repo_metrics['stars_gained_14d'] = repo_data.get('recent_stars', 0)  
        if 'recent_commits' in repo_data:
            repo_metrics['commits_14d'] = repo_data.get('recent_commits', 0)
        if 'contributor_count' in repo_data:
            repo_metrics['contributors_30d'] = repo_data.get('contributor_count', 0)
            
        # Log initial metrics from repo_data
        if self.logger:
            self.logger.debug(f"Initial metrics from repo_data: stars={repo_metrics['stars']}, commits={repo_metrics['commits_14d']}, contributors={repo_metrics['contributors_30d']}")
        
        # Check if we have a GitHub client
        if not self.github:
            if self.logger:
                self.logger.warning(f"No GitHub client available for {repo_data.get('full_name')} - using only provided metrics")
        elif 'full_name' not in repo_data:
            if self.logger:
                self.logger.warning(f"Missing full_name in repo_data - cannot fetch GitHub data")
        else:
            # We have both a GitHub client and full_name, try to fetch data
            if self.logger:
                self.logger.debug(f"Fetching GitHub data for {repo_data.get('full_name')}")
            try:
                repo_obj = self.github.get_repo(repo_data['full_name'])
                
                # Extract basic metrics
                repo_metrics['stars'] = repo_obj.stargazers_count
                repo_metrics['forks'] = repo_obj.forks_count
                
                if self.logger:
                    self.logger.debug(f"Successfully fetched GitHub data: stars={repo_obj.stargazers_count}, forks={repo_obj.forks_count}")
                
                # Get recent activity
                since_date_14d = datetime.datetime.now(timezone.utc) - timedelta(days=14)
                since_date_30d = datetime.datetime.now(timezone.utc) - timedelta(days=30)
                
                # Try to get commit count (last 14 days)
                try:
                    commits = list(repo_obj.get_commits(since=since_date_14d))
                    repo_metrics['commits_14d'] = len(commits)
                except Exception as e:
                    if self.logger:
                        self.logger.debug(f"Couldn't fetch commits for {repo_data['full_name']}: {str(e)}")
                
                # Try to get contributor count (last 30 days)
                try:
                    # This is an approximation since GitHub API doesn't directly support time-based contributor filtering
                    contributors = list(repo_obj.get_contributors())
                    repo_metrics['contributors_30d'] = len(contributors[:10])  # Limit to first 10 for performance
                except Exception as e:
                    if self.logger:
                        self.logger.debug(f"Couldn't fetch contributors for {repo_data['full_name']}: {str(e)}")
                
                # Star velocity estimate - using events isn't reliable through API
                # Using stargazers with pagination is too expensive for many calls
                # So we'll use a heuristic based on repo age and stars
                creation_date = repo_obj.created_at
                days_since_creation = (datetime.datetime.now(timezone.utc) - creation_date).days
                if days_since_creation > 0:
                    # Very rough estimate - better than 0
                    avg_daily_stars = repo_metrics['stars'] / max(1, days_since_creation)
                    repo_metrics['stars_gained_14d'] = int(avg_daily_stars * 14)
                    # For newer trending repos, bump this up
                    if days_since_creation <= 30:
                        repo_metrics['stars_gained_14d'] = int(repo_metrics['stars_gained_14d'] * 2)
                
                # Same approach for forks
                if days_since_creation > 0:
                    avg_daily_forks = repo_metrics['forks'] / max(1, days_since_creation)
                    repo_metrics['forks_gained_14d'] = int(avg_daily_forks * 14)
                
                # For issue resolution, get a sample
                try:
                    closed_issues = list(repo_obj.get_issues(state='closed', sort='updated', direction='desc')[:20])
                    if closed_issues:
                        total_days = 0
                        count = 0
                        for issue in closed_issues:
                            if issue.created_at and issue.closed_at:
                                resolution_days = (issue.closed_at - issue.created_at).days
                                if 0 <= resolution_days <= 90:  # Skip outliers
                                    total_days += resolution_days
                                    count += 1
                        if count > 0:
                            repo_metrics['avg_issue_resolution_days'] = total_days / count
                except Exception as e:
                    if self.logger:
                        self.logger.debug(f"Couldn't fetch issues for {repo_data['full_name']}: {str(e)}")
                        
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error getting repo object: {str(e)}")
                    if isinstance(e, RateLimitExceededException):
                        self.logger.warning(f"GitHub API rate limit exceeded - check your token permissions and limits")
                    self.logger.info(f"Falling back to repo_data metrics: {repo_data.get('stars', 0)} stars, {repo_data.get('recent_commits', 0)} commits")
        
        # 1. Commit Surge (3 pts): 10+ commits in 14 days, 3+ with "feat:" or "add"
        commit_score, commit_details = self._score_commit_surge(repo_data, repo_obj)
        details['commit_surge'] = commit_score
        if commit_details:
            details['signals'].append(commit_details)
        score += commit_score
        
        # 2. Star Velocity (3 pts): 10+ stars gained in 14 days
        star_score, star_details = self._score_star_velocity(repo_data, repo_obj)
        details['star_velocity'] = star_score
        if star_details:
            details['signals'].append(star_details)
        score += star_score
        
        # 3. Team Traction (2 pts): 2-5 contributors with 5+ commits each in 30 days
        team_score, team_details = self._score_team_traction(repo_data, repo_obj)
        details['team_traction'] = team_score
        if team_details:
            details['signals'].append(team_details)
        score += team_score
        
        # 4. Dev Ecosystem Fit (2 pts): Python/TypeScript/Rust OR topics like "devops", "cli", "sdk"
        ecosystem_score, ecosystem_details = self._score_dev_ecosystem_fit(repo_data, repo_obj)
        details['dev_ecosystem_fit'] = ecosystem_score
        if ecosystem_details:
            details['signals'].append(ecosystem_details)
        score += ecosystem_score
        
        # Add metrics to the return value so they can be included in the output
        details['metrics'] = repo_metrics
        
        # Diagnostic logging to help identify scoring issues
        if self.logger:
            self.logger.info(f"Scoring complete for {repo_data.get('full_name')}: score={score}, metrics={repo_metrics}")
            
            # Warning if all signals are zero - likely indicates data problem
            if score == 0:
                self.logger.warning(f"Zero score for {repo_data.get('full_name')} - check GitHub API access and data quality")
            
            # Schema consistency check - team_traction vs new_contributors
            if 'team_traction' in details and details['team_traction'] > 0:
                self.logger.debug(f"Note: Using 'team_traction' field (value: {details['team_traction']}) - ensure schema expects this field name")
        
        return score, details
    
    def _score_commit_surge(self, repo_data: Dict[str, Any], repo_obj=None) -> Tuple[int, str]:
        """Score repository based on commit surge."""
        # If we have direct commit data, use it
        recent_commits = repo_data.get('recent_commits', 0)
        feature_commits = repo_data.get('feature_commits', 0)
        
        # If we have a repo object, get more detailed commit info
        if repo_obj:
            try:
                # Get commits from last 14 days
                since_date = datetime.datetime.now(timezone.utc) - timedelta(days=self.momentum_days)
                commits = list(repo_obj.get_commits(since=since_date))
                
                recent_commits = len(commits)
                
                # Count feature commits (looking for feat: or add in message)
                feature_commits = sum(1 for c in commits 
                                   if c.commit.message and 
                                   ('feat:' in c.commit.message.lower() or 
                                    'add ' in c.commit.message.lower()))
                
                if self.logger and recent_commits > 0:
                    self.logger.debug(f"Found {recent_commits} recent commits ({feature_commits} feature commits) for {repo_obj.full_name}")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error analyzing commits: {str(e)} - check GitHub token permissions")
                # Attempt to fallback to repo_data values if GitHub API call failed
                if 'recent_commits' in repo_data:
                    if self.logger:
                        self.logger.info(f"Falling back to repo_data for commits: {repo_data['recent_commits']}")
                    recent_commits = repo_data['recent_commits']
        
        # Score based on criteria
        score = 0
        if recent_commits >= 10:
            score += 1
            if recent_commits >= 15:
                score += 1
        
        if feature_commits >= 3:
            score += 1
            
        # Generate details text
        details = ""
        if score > 0:
            details = f"{recent_commits} commits in last 14 days"
            if feature_commits > 0:
                details += f" ({feature_commits} feature commits)"
                
        return score, details
    
    def _score_star_velocity(self, repo_data: Dict[str, Any], repo_obj=None) -> Tuple[int, str]:
        """Score repository based on star velocity."""
        # Direct star velocity data if available
        recent_stars = repo_data.get('recent_stars', 0)
        
        # If we have trending star data from GitHub trending
        if 'trending_stars' in repo_data:
            trending_stars = repo_data['trending_stars']
            timespan = repo_data.get('trending_timespan', 'weekly')
            
            # Adjust based on timespan
            if timespan == 'daily':
                recent_stars = trending_stars * 7  # Estimate weekly from daily
            elif timespan == 'weekly':
                recent_stars = trending_stars
            elif timespan == 'monthly':
                recent_stars = trending_stars / 4  # Estimate weekly from monthly
        
        # Score based on criteria
        score = 0
        if recent_stars >= 10:
            score += 1
            if recent_stars >= 20:
                score += 1
                if recent_stars >= 50:
                    score += 1
                    
        # Generate details text
        details = ""
        if score > 0:
            details = f"{recent_stars} stars gained in last 14 days"
                
        return score, details
    
    def _score_team_traction(self, repo_data: Dict[str, Any], repo_obj=None) -> Tuple[int, str]:
        """Score repository based on team traction."""
        # Direct contributor data if available
        total_contributors = repo_data.get('contributor_count', 0)
        active_contributors = repo_data.get('active_contributors', 0)
        
        # If we have a repo object, get more detailed contributor info
        if repo_obj:
            try:
                # Get all contributors
                contributors = list(repo_obj.get_contributors())
                total_contributors = len(contributors)
                
                # Count contributors with 5+ commits
                # This is a simplification - ideally we'd check timeframe
                active_contributors = 0
                for contrib in contributors:
                    if contrib.contributions >= 5:
                        active_contributors += 1
                        
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error analyzing contributors: {str(e)}")
        
        # Score based on criteria
        score = 0
        
        # Check if in the sweet spot of 2-5 active contributors
        if 2 <= active_contributors <= 5:
            score += 1
            
        # Check for good contribution activity
        if active_contributors >= 2 and active_contributors == total_contributors:
            score += 1  # All contributors are active (team cohesion)
        
        # Generate details text
        details = ""
        if score > 0:
            details = f"{active_contributors} active contributors"
            if active_contributors != total_contributors:
                details += f" out of {total_contributors} total"
                
        return score, details
    
    def _score_dev_ecosystem_fit(self, repo_data: Dict[str, Any], repo_obj=None) -> Tuple[int, str]:
        """Score repository based on developer ecosystem fit."""
        # Check language
        language = repo_data.get('language', '').lower() if repo_data.get('language') else ''
        
        # Check topics
        topics = repo_data.get('topics', [])
        if not topics and repo_obj:
            try:
                topics = repo_obj.get_topics()
            except Exception:
                topics = []
        
        # Score based on criteria
        score = 0
        
        # Check if language is a developer-focused language
        if language in self.dev_languages:
            score += 1
            
        # Check if topics include developer tool topics
        dev_tool_topics = [t for t in topics if t.lower() in self.dev_topics]
        if dev_tool_topics:
            score += 1
        
        # Generate details text
        details = ""
        if score > 0:
            details_parts = []
            if language in self.dev_languages:
                details_parts.append(f"{language} language")
                
            if dev_tool_topics:
                details_parts.append(f"{', '.join(dev_tool_topics)} topics")
                
            details = ", ".join(details_parts)
                
        return score, details
