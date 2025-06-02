"""
Startup potential scoring system for GitHub repositories.
"""
import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from ..utils import Config, setup_logger


class StartupScorer:
    """
    Scores GitHub repositories for startup potential using a 50-point algorithm.
    """
    
    def __init__(self, config=None, repositories=None, hn_discussions=None):
        """
        Initialize the startup scorer with configuration.
        
        Args:
            config: Configuration manager (optional)
            repositories: Repository data from GitHubCollector (optional)
            hn_discussions: Hacker News discussions data (optional)
        """
        self.config = config if config is not None else Config()
        self.logger = setup_logger(self.__class__.__name__)
        self.repositories = repositories or []
        self.hn_discussions = hn_discussions or []
        
        # Load scoring parameters from config
        self.scoring_params = self.config.get('scoring', {})
        self.startup_keywords = self.config.get('startup_keywords', [])
        
    def score_repository(self, repo_data: Dict[str, Any], hn_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score a repository for startup potential.
        
        Args:
            repo_data: Repository data from GitHubCollector
            hn_data: Hacker News data related to the repository (optional)
            
        Returns:
            Dictionary with scores and breakdown
        """
        # Initialize score components
        repo_score = self._score_repository_signals(repo_data)
        org_score = self._score_organization_signals(repo_data)
        community_score = self._score_community_signals(repo_data, hn_data)
        
        # Calculate total score
        total_score = repo_score['total'] + org_score['total'] + community_score['total']
        
        # Determine confidence level
        confidence = self._calculate_confidence_level(total_score)
        
        # Compile final results
        return {
            'total_score': total_score,
            'repository_score': repo_score,
            'organization_score': org_score,
            'community_score': community_score,
            'confidence_level': confidence,
            'repository': repo_data['full_name'],
            'scored_at': datetime.datetime.now().isoformat()
        }
        
    def _score_repository_signals(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score repository signals for startup potential.
        
        Args:
            repo_data: Repository data from GitHubCollector
            
        Returns:
            Dictionary with repository score and breakdown
        """
        scores = {}
        params = self.scoring_params.get('repository', {})
        
        # Recent creation (≤90 days)
        created_at = datetime.datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
        age_days = (datetime.datetime.now().replace(tzinfo=None) - created_at.replace(tzinfo=None)).days
        repo_age_threshold = self.config.get('github.repo_age_threshold', 90)
        
        if age_days <= repo_age_threshold:
            scores['recent_creation'] = params.get('recent_creation', 3)
        else:
            scores['recent_creation'] = 0
            
        # Professional language (Python/Go/TypeScript/etc)
        professional_languages = self.config.get('github.language_filter', [
            'python', 'javascript', 'typescript', 'go', 'rust',
            'java', 'kotlin', 'swift', 'ruby', 'php'
        ])
        
        if repo_data.get('language') and repo_data['language'].lower() in [l.lower() for l in professional_languages]:
            scores['professional_language'] = params.get('professional_language', 2)
        else:
            scores['professional_language'] = 0
            
        # CI/CD setup
        if repo_data.get('ci_cd_setup'):
            scores['ci_cd_setup'] = params.get('ci_cd_setup', 2)
        else:
            scores['ci_cd_setup'] = 0
            
        # Quality documentation
        readme_score = repo_data.get('readme_quality', {}).get('score', 0)
        if readme_score >= 1.5:
            scores['quality_documentation'] = params.get('quality_documentation', 2)
        elif readme_score >= 1.0:
            scores['quality_documentation'] = params.get('quality_documentation', 2) * 0.5
        else:
            scores['quality_documentation'] = 0
            
        # Active development (10+ commits/week)
        weekly_commits = repo_data.get('commit_activity', {}).get('weekly_commits', 0)
        if weekly_commits >= 10:
            scores['active_development'] = params.get('active_development', 3)
        elif weekly_commits >= 5:
            scores['active_development'] = params.get('active_development', 3) * 0.5
        else:
            scores['active_development'] = 0
            
        # External website
        if repo_data.get('external_website'):
            scores['external_website'] = params.get('external_website', 2)
        else:
            scores['external_website'] = 0
            
        # Startup keywords in description
        description = repo_data.get('description', '').lower() if repo_data.get('description') else ''
        topics = [t.lower() for t in repo_data.get('topics', [])]
        
        keyword_count = 0
        for keyword in self.startup_keywords:
            if keyword.lower() in description or keyword.lower() in topics:
                keyword_count += 1
                
        if keyword_count >= 2:
            scores['startup_keywords'] = params.get('startup_keywords', 3)
        elif keyword_count == 1:
            scores['startup_keywords'] = params.get('startup_keywords', 3) * 0.5
        else:
            scores['startup_keywords'] = 0
            
        # Y Combinator mentions
        yc_keywords = ['yc ', 'y combinator', 'ycombinator', 'y-combinator', 'w20', 's20', 'w21', 's21', 'w22', 's22', 'w23', 's23']
        
        has_yc = False
        for keyword in yc_keywords:
            if description and keyword.lower() in description.lower():
                has_yc = True
                break
            for topic in topics:
                if keyword.lower() in topic:
                    has_yc = True
                    break
                    
        if has_yc:
            scores['y_combinator_mentions'] = params.get('y_combinator_mentions', 2)
        else:
            scores['y_combinator_mentions'] = 0
            
        # Tests present
        if repo_data.get('has_tests'):
            scores['tests_present'] = params.get('tests_present', 1)
        else:
            scores['tests_present'] = 0
            
        # Calculate total repository score
        total = sum(scores.values())
        
        return {
            'total': total,
            'max_possible': 20,
            'percentage': (total / 20) * 100,
            'breakdown': scores
        }
        
    def _score_organization_signals(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score organization signals for startup potential.
        
        Args:
            repo_data: Repository data from GitHubCollector
            
        Returns:
            Dictionary with organization score and breakdown
        """
        scores = {}
        params = self.scoring_params.get('organization', {})
        org_data = repo_data.get('organization', {})
        
        # If this is not an organization repository, most scores will be 0
        if not org_data or repo_data['owner']['type'] != 'Organization':
            return {
                'total': 0,
                'max_possible': 15,
                'percentage': 0,
                'breakdown': {
                    'recent_creation': 0,
                    'team_size': 0,
                    'multiple_repos': 0,
                    'professional_profile': 0,
                    'organization_website': 0,
                    'hiring_indicators': 0
                }
            }
            
        # Recent org creation
        try:
            if org_data.get('created_at'):
                created_at = datetime.datetime.fromisoformat(org_data['created_at'].replace('Z', '+00:00'))
                age_days = (datetime.datetime.now().replace(tzinfo=None) - created_at.replace(tzinfo=None)).days
                
                if age_days <= 365:  # 1 year
                    scores['recent_creation'] = params.get('recent_creation', 3)
                elif age_days <= 730:  # 2 years
                    scores['recent_creation'] = params.get('recent_creation', 3) * 0.5
                else:
                    scores['recent_creation'] = 0
            else:
                scores['recent_creation'] = 0
        except (ValueError, TypeError):
            scores['recent_creation'] = 0
            
        # Team size 2-15 members
        team_size = org_data.get('team_size', 0)
        if 2 <= team_size <= 15:
            scores['team_size'] = params.get('team_size', 3)
        elif 16 <= team_size <= 30:
            scores['team_size'] = params.get('team_size', 3) * 0.5
        else:
            scores['team_size'] = 0
            
        # Multiple repositories
        public_repos = org_data.get('public_repos', 0)
        if 2 <= public_repos <= 10:
            scores['multiple_repos'] = params.get('multiple_repos', 2)
        elif public_repos > 10:
            scores['multiple_repos'] = params.get('multiple_repos', 2) * 0.5
        else:
            scores['multiple_repos'] = 0
            
        # Professional org profile
        has_name = bool(org_data.get('name'))
        has_bio = bool(org_data.get('bio'))
        has_email = bool(org_data.get('email'))
        has_location = bool(org_data.get('location'))
        
        profile_completeness = sum([has_name, has_bio, has_email, has_location])
        if profile_completeness >= 3:
            scores['professional_profile'] = params.get('professional_profile', 2)
        elif profile_completeness >= 2:
            scores['professional_profile'] = params.get('professional_profile', 2) * 0.5
        else:
            scores['professional_profile'] = 0
            
        # Organization website
        if org_data.get('blog') or org_data.get('has_website'):
            scores['organization_website'] = params.get('organization_website', 2)
        else:
            scores['organization_website'] = 0
            
        # Hiring indicators
        if org_data.get('hiring_indicators'):
            scores['hiring_indicators'] = params.get('hiring_indicators', 3)
        else:
            scores['hiring_indicators'] = 0
            
        # Calculate total organization score
        total = sum(scores.values())
        
        return {
            'total': total,
            'max_possible': 15,
            'percentage': (total / 15) * 100,
            'breakdown': scores
        }
        
    def _score_community_signals(
        self,
        repo_data: Dict[str, Any],
        hn_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score community signals for startup potential.
        
        Args:
            repo_data: Repository data from GitHubCollector
            hn_data: Hacker News data related to the repository (optional)
            
        Returns:
            Dictionary with community score and breakdown
        """
        scores = {}
        params = self.scoring_params.get('community', {})
        
        # Hacker News discussion
        if hn_data:
            hn_score = hn_data.get('hn_score', 0)
            comment_count = hn_data.get('comment_count', 0)
            
            # Scale HN score based on points and comments
            scaled_score = min(5, (hn_score / 30) * params.get('hacker_news_discussion', 5))
            scores['hacker_news_discussion'] = scaled_score
        else:
            scores['hacker_news_discussion'] = 0
            
        # Rapid star growth
        stars = repo_data.get('stargazers_count', 0)
        age_days = (datetime.datetime.now().replace(tzinfo=None) - 
                  datetime.datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)).days
        
        # Calculate stars per day
        stars_per_day = stars / max(1, age_days)
        
        # Score based on stars per day
        if stars_per_day >= 2.0:
            scores['star_growth'] = params.get('star_growth', 3)
        elif stars_per_day >= 1.0:
            scores['star_growth'] = params.get('star_growth', 3) * 0.66
        elif stars_per_day >= 0.5:
            scores['star_growth'] = params.get('star_growth', 3) * 0.33
        else:
            scores['star_growth'] = 0
            
        # External contributors
        external_count = repo_data.get('contributors', {}).get('external_count', 0)
        if external_count >= 3:
            scores['external_contributors'] = params.get('external_contributors', 2)
        elif external_count >= 1:
            scores['external_contributors'] = params.get('external_contributors', 2) * 0.5
        else:
            scores['external_contributors'] = 0
            
        # Issue engagement
        issue_count = repo_data.get('open_issues_count', 0)
        if issue_count >= 5:
            scores['issue_engagement'] = params.get('issue_engagement', 2)
        elif issue_count >= 2:
            scores['issue_engagement'] = params.get('issue_engagement', 2) * 0.5
        else:
            scores['issue_engagement'] = 0
            
        # Fork activity
        fork_count = repo_data.get('forks_count', 0)
        if fork_count >= 3:
            scores['fork_activity'] = params.get('fork_activity', 2)
        elif fork_count >= 1:
            scores['fork_activity'] = params.get('fork_activity', 2) * 0.5
        else:
            scores['fork_activity'] = 0
            
        # Social mentions (simplified, would be more comprehensive in a production system)
        # For now, we'll consider topics like "trending" as an indicator
        topics = [t.lower() for t in repo_data.get('topics', [])]
        social_topics = ['trending', 'popular', 'featured', 'producthunt']
        
        has_social_mentions = any(topic in topics for topic in social_topics)
        if has_social_mentions:
            scores['social_mentions'] = params.get('social_mentions', 1)
        else:
            scores['social_mentions'] = 0
            
        # Calculate total community score
        total = sum(scores.values())
        
        return {
            'total': total,
            'max_possible': 15,
            'percentage': (total / 15) * 100,
            'breakdown': scores
        }
        
    def _calculate_confidence_level(self, total_score: float) -> str:
        """
        Calculate confidence level based on total score.
        
        Args:
            total_score: The total score (0-50)
            
        Returns:
            Confidence level string: 'high', 'medium', or 'low'
        """
        if total_score >= 35:  # 70% or higher
            return 'high'
        elif total_score >= 25:  # 50% or higher
            return 'medium'
        else:
            return 'low'
        
    def score_repositories(self) -> List[Dict[str, Any]]:
        """
        Score all repositories for startup potential.
        
        Returns:
            List of repositories with their scores and breakdowns
        """
        self.logger.info(f"Scoring {len(self.repositories)} repositories for startup potential")
        
        scored_repos = []
        for repo in self.repositories:
            # Find related HN discussions for this repo
            repo_url = repo.get('url', '')
            related_hn = next(
                (hn for hn in self.hn_discussions if repo_url in hn.get('urls', [])), 
                None
            )
            
            # Score the repository
            scored_repo = self.score_repository(repo, related_hn)
            scored_repos.append(scored_repo)
            
        self.logger.info(f"Completed scoring {len(scored_repos)} repositories")
        return scored_repos
