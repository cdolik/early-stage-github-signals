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
        self.accelerator_keywords = [
            'y combinator', 'ycombinator', 'yc', 'techstars', '500 startups', 
            'seedcamp', 'startup chile', 'angelpad', 'dreamit', 'boost vc',
            'founders factory', 'boomtown', 'amplify', 'accelerator', 'incubator'
        ]
        
    def score_repository(self, repo_data: Dict[str, Any], hn_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Score a repository for startup potential.
        
        Args:
            repo_data: Repository data from GitHubCollector
            hn_data: Hacker News discussion data (optional)
            
        Returns:
            Repository data with scores and insights
        """
        self.logger.debug(f"Scoring repository: {repo_data.get('full_name')}")
        
        # Create copy of repo data to avoid modifying original
        scored_repo = repo_data.copy()
        
        # Score repository signals
        repository_result = self._score_repository_signals(scored_repo)
        repository_score = repository_result.get('total', 0)
        repository_details = repository_result.get('details', {})
        
        # Score organization signals
        organization_result = self._score_organization_signals(scored_repo)
        organization_score = organization_result.get('total', 0)
        organization_details = organization_result.get('details', {})
        
        # Score community signals
        community_result = self._score_community_signals(scored_repo, hn_data)
        community_score = community_result.get('total', 0)
        community_details = community_result.get('details', {})
        
        # Calculate total score
        total_score = repository_score + organization_score + community_score
        
        # Determine potential level
        potential_level = self._get_potential_level(total_score)
        
        # Add scores to repository data
        scored_repo['repository_score'] = repository_score
        scored_repo['organization_score'] = organization_score
        scored_repo['community_score'] = community_score
        scored_repo['total_score'] = total_score
        scored_repo['potential_level'] = potential_level
        scored_repo['score_details'] = {
            'repository': repository_details,
            'organization': organization_details,
            'community': community_details
        }
        
        # Generate insights
        insights = self._generate_insights(
            scored_repo, 
            repository_details,
            organization_details,
            community_details,
            total_score
        )
        scored_repo['insights'] = insights
        
        return scored_repo
        
    def _score_repository_signals(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score repository signals (max 20 points).
        
        Args:
            repo: Repository data
            
        Returns:
            Dictionary with total score and details
        """
        self.logger.debug(f"Scoring repository signals for: {repo.get('full_name')}")
        
        score = 0
        details = {}
        max_points = self.scoring_params.get('repository', {}).get('max_points', 20)
        
        # Recent creation (0-3 points)
        recent_creation_score = 0
        if repo.get('created_at'):
            created_at = datetime.datetime.fromisoformat(repo.get('created_at').replace('Z', '+00:00'))
            now = datetime.datetime.now(datetime.timezone.utc)
            days_since_creation = (now - created_at).days
            
            if days_since_creation <= 30:
                recent_creation_score = 3  # Very recent
            elif days_since_creation <= 90:
                recent_creation_score = 2  # Recent
            elif days_since_creation <= 180:
                recent_creation_score = 1  # Somewhat recent
        
        score += recent_creation_score
        details['recent_creation'] = {
            'points': recent_creation_score,
            'reason': f"Repository created {days_since_creation if 'days_since_creation' in locals() else 'unknown'} days ago"
        }
        
        # Professional language (0-2 points)
        professional_language_score = 0
        professional_languages = ['TypeScript', 'Python', 'Go', 'Swift', 'Kotlin', 'Rust', 'JavaScript', 'Java', 'C#', 'C++']
        
        language = repo.get('language')
        if language in professional_languages:
            professional_language_score = 2
        elif language:  # Any other language
            professional_language_score = 1
        
        score += professional_language_score
        details['professional_language'] = {
            'points': professional_language_score,
            'reason': f"Using {language}" if language else "No primary language detected"
        }
        
        # CI/CD setup (0-2 points)
        ci_cd_score = 2 if repo.get('has_ci_cd') else 0
        score += ci_cd_score
        details['ci_cd_setup'] = {
            'points': ci_cd_score,
            'reason': "CI/CD workflow detected" if ci_cd_score else "No CI/CD setup"
        }
        
        # Quality documentation (0-2 points)
        readme = repo.get('readme', {})
        readme_quality_score = min(2, round(readme.get('quality_score', 0) / 2.5))
        
        score += readme_quality_score
        details['quality_documentation'] = {
            'points': readme_quality_score,
            'reason': f"README quality score: {readme.get('quality_score', 0)}/5"
        }
        
        # Active development (0-3 points)
        active_development_score = 0
        commit_activity = repo.get('commit_activity', {})
        
        if commit_activity.get('active_development'):
            # Very active (several commits in past 7 days)
            if commit_activity.get('recent_commits', 0) >= 10:
                active_development_score = 3
            # Moderately active
            elif commit_activity.get('recent_commits', 0) >= 5:
                active_development_score = 2
            # Somewhat active
            else:
                active_development_score = 1
        
        score += active_development_score
        details['active_development'] = {
            'points': active_development_score,
            'reason': f"{commit_activity.get('recent_commits', 0)} recent commits"
        }
        
        # External website (0-2 points)
        website_score = 2 if repo.get('has_website') else 0
        score += website_score
        details['external_website'] = {
            'points': website_score,
            'reason': "External website found" if website_score else "No external website"
        }
        
        # Startup keywords (0-3 points)
        startup_keywords_score = self._assess_startup_keywords(repo)
        score += startup_keywords_score
        details['startup_keywords'] = {
            'points': startup_keywords_score,
            'reason': f"Found {startup_keywords_score} startup-related keywords"
        }
        
        # Accelerator mentions (0-2 points)
        accelerator_score = self._assess_accelerator_mentions(repo)
        score += accelerator_score
        details['accelerator_mentions'] = {
            'points': accelerator_score,
            'reason': "Accelerator program mentioned" if accelerator_score else "No accelerator mentions"
        }
        
        # Tests present (0-1 point)
        tests_score = 1 if repo.get('has_tests') else 0
        score += tests_score
        details['tests_present'] = {
            'points': tests_score,
            'reason': "Test suite detected" if tests_score else "No tests detected"
        }
        
        # Ensure we don't exceed max points
        score = min(score, max_points)
        
        return {
            'total': score,
            'max': max_points,
            'details': details
        }
    
    def _score_organization_signals(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score organization signals (max 15 points).
        
        Args:
            repo: Repository data
            
        Returns:
            Dictionary with total score and details
        """
        self.logger.debug(f"Scoring organization signals for: {repo.get('full_name')}")
        
        score = 0
        details = {}
        max_points = self.scoring_params.get('organization', {}).get('max_points', 15)
        
        # If no organization, return minimal score
        if not repo.get('organization'):
            return {
                'total': 0,
                'max': max_points,
                'details': {'no_organization': {'points': 0, 'reason': 'Individual repository, not an organization'}}
            }
        
        org_details = repo.get('org_details', {})
        
        # Recent organization creation (0-3 points)
        recent_creation_score = 0
        if org_details.get('recent_creation'):
            recent_creation_score = 3
        elif org_details.get('created_at'):
            created_at = datetime.datetime.fromisoformat(org_details.get('created_at').replace('Z', '+00:00'))
            days_since_creation = (datetime.datetime.now() - created_at).days
            
            if days_since_creation <= 365:  # Within a year
                recent_creation_score = 2
            elif days_since_creation <= 730:  # Within two years
                recent_creation_score = 1
        
        score += recent_creation_score
        details['recent_creation'] = {
            'points': recent_creation_score,
            'reason': "Organization recently created" if recent_creation_score else "Established organization"
        }
        
        # Team size (0-3 points)
        team_size_score = 0
        team_size = org_details.get('total_members', 0)
        
        if team_size >= 5:
            team_size_score = 3  # Good size for a startup
        elif team_size >= 3:
            team_size_score = 2  # Small team
        elif team_size >= 1:
            team_size_score = 1  # Solo founder or very small
        
        score += team_size_score
        details['team_size'] = {
            'points': team_size_score,
            'reason': f"Organization has {team_size} members"
        }
        
        # Multiple repositories (0-2 points)
        multiple_repos_score = 0
        public_repos = org_details.get('public_repos', 0)
        
        if public_repos >= 5:
            multiple_repos_score = 2  # Very active organization
        elif public_repos >= 2:
            multiple_repos_score = 1  # Multiple projects
        
        score += multiple_repos_score
        details['multiple_repos'] = {
            'points': multiple_repos_score,
            'reason': f"Organization has {public_repos} public repositories"
        }
        
        # Professional profile (0-2 points)
        professional_profile_score = 0
        
        # Check for description and contact info
        if org_details.get('description'):
            professional_profile_score += 1
        
        # Check for social media presence
        if org_details.get('twitter_username') or org_details.get('blog') or org_details.get('email'):
            professional_profile_score += 1
        
        score += professional_profile_score
        details['professional_profile'] = {
            'points': professional_profile_score,
            'reason': "Complete organization profile" if professional_profile_score == 2 else 
                    "Partial organization profile" if professional_profile_score == 1 else
                    "Minimal organization profile"
        }
        
        # Website (0-2 points)
        website_score = 2 if org_details.get('has_website') else 0
        score += website_score
        details['website'] = {
            'points': website_score,
            'reason': "Organization has website" if website_score else "No organization website"
        }
        
        # Hiring indicators (0-3 points)
        hiring_score = 0
        
        # Direct hiring indicator
        if org_details.get('hiring_indicators'):
            hiring_score = 3
        # Recent commits might indicate active hiring
        elif repo.get('commit_activity', {}).get('active_development'):
            hiring_score = 1
        
        score += hiring_score
        details['hiring_indicators'] = {
            'points': hiring_score,
            'reason': "Organization is actively hiring" if hiring_score == 3 else
                    "Some hiring activity detected" if hiring_score == 1 else
                    "No hiring indicators"
        }
        
        # Ensure we don't exceed max points
        score = min(score, max_points)
        
        return {
            'total': score,
            'max': max_points,
            'details': details
        }
    
    def _score_community_signals(
        self,
        repo: Dict[str, Any],
        hn_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Score community signals (max 15 points).
        
        Args:
            repo: Repository data
            hn_data: Hacker News discussion data (optional)
            
        Returns:
            Dictionary with total score and details
        """
        self.logger.debug(f"Scoring community signals for: {repo.get('full_name')}")
        
        score = 0
        details = {}
        max_points = self.scoring_params.get('community', {}).get('max_points', 15)
        
        # Hacker News discussion (0-5 points)
        hn_score = 0
        hn_reason = "No Hacker News discussion found"
        
        if hn_data:
            points = hn_data.get('points', 0)
            comments = hn_data.get('comments', 0)
            
            if points >= 100 or comments >= 50:
                hn_score = 5  # Substantial discussion
            elif points >= 50 or comments >= 25:
                hn_score = 3  # Moderate discussion
            elif points > 0 or comments > 0:
                hn_score = 1  # Some discussion
            
            hn_reason = f"HN post with {points} points and {comments} comments"
        
        score += hn_score
        details['hn_discussion'] = {
            'points': hn_score,
            'reason': hn_reason
        }
        
        # Star growth (0-3 points)
        star_growth_score = 0
        stars = repo.get('stars', 0)
        
        if stars >= 100:
            star_growth_score = 3  # High traction
        elif stars >= 50:
            star_growth_score = 2  # Good traction
        elif stars >= 10:
            star_growth_score = 1  # Some traction
        
        score += star_growth_score
        details['star_growth'] = {
            'points': star_growth_score,
            'reason': f"{stars} stars on GitHub"
        }
        
        # External contributors (0-2 points)
        contributors_score = 0
        external_contributors = repo.get('contributors', {}).get('external_contributors', 0)
        
        if external_contributors >= 5:
            contributors_score = 2  # Significant outside contribution
        elif external_contributors >= 1:
            contributors_score = 1  # Some outside contribution
        
        score += contributors_score
        details['external_contributors'] = {
            'points': contributors_score,
            'reason': f"{external_contributors} external contributors"
        }
        
        # Issue engagement (0-2 points)
        issue_score = 0
        open_issues = repo.get('open_issues', 0)
        
        # We don't have closed issues data, so this is an approximation
        if open_issues >= 10:
            issue_score = 2  # Active issue tracker
        elif open_issues >= 5:
            issue_score = 1  # Some issue activity
        
        score += issue_score
        details['issue_engagement'] = {
            'points': issue_score,
            'reason': f"{open_issues} open issues"
        }
        
        # Fork activity (0-2 points)
        fork_score = 0
        forks = repo.get('forks', 0)
        
        if forks >= 10:
            fork_score = 2  # Significant fork activity
        elif forks >= 5:
            fork_score = 1  # Some fork activity
        
        score += fork_score
        details['fork_activity'] = {
            'points': fork_score,
            'reason': f"{forks} forks"
        }
        
        # Social mentions / Product Hunt (0-1 point)
        # This is a placeholder since we don't have actual Product Hunt data
        product_hunt_data = repo.get('product_hunt_data', None)
        
        # Product Hunt signals (1 point)
        ph_score = 0
        if product_hunt_data:
            ph_score = 1  # Basic implementation
        score += ph_score
        details['product_hunt'] = {'points': ph_score, 'reason': 'Product Hunt presence detected' if ph_score else 'No Product Hunt data'}
        
        return {
            'total': score,
            'max': max_points,
            'details': details
        }
    
    def _assess_startup_keywords(self, repo: Dict[str, Any]) -> int:
        """Assess startup keyword relevance (0-3 points)."""
        description = (repo.get('description') or '').lower()
        topics = ' '.join(repo.get('topics', [])).lower()
        text = f"{description} {topics}"
        
        matches = sum(1 for keyword in self.startup_keywords if keyword in text)
        
        if matches >= 3:
            return 3
        elif matches >= 2:
            return 2
        elif matches >= 1:
            return 1
        return 0
    
    def _assess_accelerator_mentions(self, repo: Dict[str, Any]) -> int:
        """Check for accelerator mentions (0-2 points)."""
        description = (repo.get('description') or '').lower()
        readme_content = (repo.get('readme', {}).get('content') or '').lower()
        text = f"{description} {readme_content}"
        
        for keyword in self.accelerator_keywords:
            if keyword in text:
                return 2
        return 0
    
    def _get_potential_level(self, score: int) -> str:
        """Determine potential level based on score."""
        if score >= 35:
            return "🚀 HIGH POTENTIAL"
        elif score >= 25:
            return "📈 WORTH WATCHING"
        elif score >= 15:
            return "🔍 EARLY STAGE"
        else:
            return "⚠️ LOW POTENTIAL"
    
    def _generate_insights(self, repo: Dict, repo_details: Dict, org_details: Dict, community_details: Dict, total_score: int) -> Dict:
        """Generate actionable insights."""
        strengths = []
        concerns = []
        
        # Analyze strengths
        if repo_details.get('active_development', {}).get('points', 0) >= 2:
            strengths.append("Active development")
        if org_details.get('team_size', {}).get('points', 0) >= 2:
            strengths.append("Good team size")
        if community_details.get('star_growth', {}).get('points', 0) >= 2:
            strengths.append("Strong traction")
        if repo_details.get('quality_documentation', {}).get('points', 0) >= 2:
            strengths.append("Well-documented")
        if repo_details.get('startup_keywords', {}).get('points', 0) >= 2:
            strengths.append("Clear startup focus")
        if org_details.get('hiring_indicators', {}).get('points', 0) >= 2:
            strengths.append("Actively hiring")
        if community_details.get('external_contributors', {}).get('points', 0) >= 1:
            strengths.append("Community involvement")
        if repo_details.get('ci_cd_setup', {}).get('points', 0) >= 1:
            strengths.append("Professional development setup")
            
        # Analyze concerns
        if not repo.get('has_website'):
            concerns.append("No external website")
        if repo.get('contributors', {}).get('external_contributors', 0) == 0:
            concerns.append("No external contributors")
        if repo_details.get('tests_present', {}).get('points', 0) == 0:
            concerns.append("No test suite detected")
        if org_details.get('team_size', {}).get('points', 0) == 0 and repo.get('organization'):
            concerns.append("Small team size")
        
        # Generate investment readiness assessment
        if total_score >= 35:
            investment_readiness = "High"
            summary = f"Promising startup with strong signals ({total_score}/50 points)"
        elif total_score >= 25:
            investment_readiness = "Medium"
            summary = f"Emerging startup showing potential ({total_score}/50 points)"
        else:
            investment_readiness = "Low"
            summary = f"Early project with limited startup signals ({total_score}/50 points)"
        
        return {
            'strengths': strengths,
            'concerns': concerns,
            'summary': summary,
            'investment_readiness': investment_readiness
        }
    
    def score_repositories(self) -> List[Dict[str, Any]]:
        """
        Score all repositories.
        
        Returns:
            List of repositories with scores and insights
        """
        self.logger.info(f"Scoring {len(self.repositories)} repositories")
        
        scored_repos = []
        
        for repo in self.repositories:
            # Find matching HN discussion if any
            hn_data = None
            for hn in self.hn_discussions:
                if hn.get('github_repo') == repo.get('full_name'):
                    hn_data = hn
                    break
            
            # Score repository
            scored_repo = self.score_repository(repo, hn_data)
            scored_repos.append(scored_repo)
        
        # Sort by score
        scored_repos = sorted(scored_repos, key=lambda r: r.get('total_score', 0), reverse=True)
        
        self.logger.info(f"Scored {len(scored_repos)} repositories")
        return scored_repos
