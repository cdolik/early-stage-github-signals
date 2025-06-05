"""
GitHub data collector for the Early Stage GitHub Signals platform.
"""
import os
import base64
import datetime
import time
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import requests
from github import Github, GithubException, RateLimitExceededException
from github.Repository import Repository
from github.Organization import Organization

from .base_collector import BaseCollector
from ..utils import format_date, parse_date, rate_limited_request

from .base_collector import BaseCollector
from ..utils import format_date, parse_date, rate_limited_request


class GitHubCollector(BaseCollector):
    """
    Collector for GitHub repository data.
    """
    
    def __init__(self, config=None, cache=None):
        """
        Initialize the GitHub collector.
        
        Args:
            config: Configuration manager (optional)
            cache: Cache manager (optional)
        """
        super().__init__(config, cache)
        
        # Get GitHub configuration
        self.base_url = self.config.get('github.base_url', 'https://api.github.com')
        self.token = os.environ.get('GITHUB_TOKEN')
        
        if not self.token:
            self.logger.warning("GITHUB_TOKEN not found in environment variables")
        
        # Initialize GitHub API client
        self.github = Github(self.token)
        
        # Track API call statistics
        self.api_calls = 0
        self.last_rate_limit_check = 0
        
        # Keywords for startup potential
        self.startup_keywords = self.config.get('startup_keywords', [])
        
        # Languages to focus on
        self.languages = self.config.get('github.languages', [])
        
        # Initialize session for direct API calls
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({'Authorization': f'token {self.token}'})
        
    def get_name(self) -> str:
        """
        Get the name of the collector.
        
        Returns:
            The collector name
        """
        return "GitHub"
        
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect GitHub repository data.
        
        Args:
            date_threshold: Only consider repositories created after this date
            min_stars: Minimum number of stars for repositories
            max_repos: Maximum number of repositories to collect
            language: Optional specific language to filter by
            
        Returns:
            List of repositories with basic and enriched data
        """
        self.logger.info("Collecting GitHub repositories...")
        
        # Extract parameters
        date_threshold = kwargs.get('date_threshold')
        min_stars = kwargs.get('min_stars', 5)
        max_repos = kwargs.get('max_repos', 100)
        language = kwargs.get('language')
        
        # If no specific language provided, use all configured languages
        languages_to_check = [language] if language else self.languages
        
        all_repos = []
        
        # Check each language
        for lang in languages_to_check:
            self.logger.info(f"Collecting repositories for language: {lang or 'Any'}")
            
            # Collect repositories for this language
            repos = self._collect_trending_repos(
                language=lang,
                date_threshold=date_threshold,
                min_stars=min_stars,
                max_repos=max_repos
            )
            
            all_repos.extend(repos)
            
            # Don't exceed max repos
            if len(all_repos) >= max_repos:
                self.logger.info(f"Reached maximum repositories limit ({max_repos})")
                all_repos = all_repos[:max_repos]
                break
        
        # Enrich repositories with additional data
        enriched_repos = []
        for repo_data in all_repos:
            try:
                enriched_repo = self._enrich_repository_data(repo_data)
                enriched_repos.append(enriched_repo)
            except Exception as e:
                self.logger.error(f"Error enriching repository {repo_data.get('full_name')}: {str(e)}")
        
        self.logger.info(f"Collected {len(enriched_repos)} repositories with {self.api_calls} API calls")
        
        return enriched_repos
    
    def _collect_trending_repos(
        self,
        language: Optional[str] = None,
        date_threshold: Optional[datetime.datetime] = None,
        min_stars: int = 5,
        max_repos: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Collect trending repositories based on criteria.
        
        Args:
            language: Filter by programming language
            date_threshold: Only consider repositories created after this date
            min_stars: Minimum number of stars for repositories
            max_repos: Maximum number of repositories to collect
            
        Returns:
            List of repositories with basic data
        """
        repositories = []
        
        # Prepare date filter
        date_query = ""
        if date_threshold:
            date_str = format_date(date_threshold)
            date_query = f" created:>{date_str}"
        
        # Prepare language filter
        lang_query = ""
        if language:
            lang_query = f" language:{language}"
        
        # Prepare stars filter
        stars_query = f" stars:>={min_stars}"
        
        # Build query
        query = f"is:public{date_query}{lang_query}{stars_query}"
        
        try:
            # Execute search query
            self.logger.debug(f"Executing GitHub search: {query}")
            search_results = self.github.search_repositories(query, sort="stars", order="desc")
            self.api_calls += 1
            
            # Process results
            count = 0
            for repo in search_results:
                if count >= max_repos:
                    break
                
                # Extract basic repository data
                repo_data = self._extract_basic_repo_data(repo)
                repositories.append(repo_data)
                count += 1
                
                # Check rate limits periodically
                if count % 10 == 0:
                    if not self._check_rate_limits():
                        self.logger.warning("Rate limit reached, pausing collection")
                        break
            
            self.logger.info(f"Collected {len(repositories)} repositories matching query: {query}")
            
        except RateLimitExceededException:
            self.logger.error("GitHub API rate limit exceeded")
            self._check_rate_limits(force=True)
        except GithubException as e:
            self.logger.error(f"GitHub API error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error collecting repositories: {str(e)}")
        
        return repositories
            
    def _extract_basic_repo_data(self, repo: Repository) -> Dict[str, Any]:
        """
        Extract basic data from a repository object.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with basic repository data
        """
        # Extract basic repository data
        return {
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name,
            "url": repo.html_url,
            "api_url": repo.url,
            "description": repo.description,
            "created_at": repo.created_at.isoformat() if repo.created_at else None,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "language": repo.language,
            "topics": list(repo.get_topics()),
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "watchers": repo.subscribers_count,
            "open_issues": repo.open_issues_count,
            "organization": repo.organization.login if repo.organization else None
        }
        
    def _enrich_repository_data(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich repository data with additional information.
        
        Args:
            repo_data: Basic repository data
            
        Returns:
            Dictionary with enriched repository data
        """
        self.logger.debug(f"Enriching repository: {repo_data.get('full_name')}")
        
        try:
            # Get repository object
            repo = self.github.get_repo(repo_data.get('full_name'))
            self.api_calls += 1
            
            # Get detailed repository data
            details = self.get_repository_details(repo)
            repo_data.update(details)
            
            # Get organization data if available
            org_name = repo_data.get('organization')
            if org_name:
                try:
                    org_data = self._get_organization_data(org_name)
                    repo_data['org_details'] = org_data
                except Exception as e:
                    self.logger.error(f"Error getting organization data for {org_name}: {str(e)}")
            
            # Get contributor data
            try:
                contributor_data = self._get_contributor_data(repo)
                repo_data['contributors'] = contributor_data
            except Exception as e:
                self.logger.error(f"Error getting contributor data for {repo_data.get('full_name')}: {str(e)}")
            
            return repo_data
        
        except RateLimitExceededException:
            self.logger.error("GitHub API rate limit exceeded")
            self._check_rate_limits(force=True)
            raise
        except GithubException as e:
            self.logger.error(f"GitHub API error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error enriching repository {repo_data.get('full_name')}: {str(e)}")
            raise
        
    def get_repository_details(self, repo: Repository) -> Dict[str, Any]:
        """
        Get detailed information about a repository.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with repository details
        """
        details = {}
        
        # Check for CI/CD setup
        details['has_ci_cd'] = self._has_ci_cd_setup(repo)
        
        # Check for tests
        details['has_tests'] = self._has_tests(repo)
        
        # Get README quality assessment
        readme = self._get_readme_quality(repo)
        details['readme'] = readme
        
        # Get commit activity
        commit_activity = self._get_commit_activity(repo)
        details['commit_activity'] = commit_activity
        
        # Check if repo has external website
        website_url = self._get_external_website(repo, details)
        details['website_url'] = website_url
        details['has_website'] = bool(website_url)
        
        return details
    
    def _has_ci_cd_setup(self, repo: Repository) -> bool:
        """
        Check if repository has CI/CD setup.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            True if CI/CD setup found, False otherwise
        """
        try:
            # Check for GitHub Actions workflows
            try:
                workflows_dir = repo.get_contents(".github/workflows")
                if workflows_dir and len(workflows_dir) > 0:
                    return True
            except GithubException:
                pass
            
            # Check for Travis CI
            try:
                travis_file = repo.get_contents(".travis.yml")
                if travis_file:
                    return True
            except GithubException:
                pass
            
            # Check for CircleCI
            try:
                circle_file = repo.get_contents(".circleci/config.yml")
                if circle_file:
                    return True
            except GithubException:
                pass
            
            # Check for Jenkins
            try:
                jenkins_file = repo.get_contents("Jenkinsfile")
                if jenkins_file:
                    return True
            except GithubException:
                pass
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking CI/CD setup: {str(e)}")
            return False
            
    def _has_tests(self, repo: Repository) -> bool:
        """
        Check if repository has tests.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            True if tests found, False otherwise
        """
        try:
            # Check common test directories
            test_dirs = ["test", "tests", "spec", "specs"]
            for test_dir in test_dirs:
                try:
                    test_contents = repo.get_contents(test_dir)
                    if test_contents and len(test_contents) > 0:
                        return True
                except GithubException:
                    continue
            
            return False
        except Exception as e:
            self.logger.error(f"Error checking for tests: {str(e)}")
            return False
            
    def _get_readme_quality(self, repo: Repository) -> Dict[str, Any]:
        """
        Get README quality assessment.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with README quality assessment
        """
        result = {
            'exists': False,
            'length': 0,
            'quality_score': 0,
            'has_images': False,
            'content': None
        }
        
        try:
            # Try to get README content
            readme_content = None
            for readme_name in ["README.md", "README", "Readme.md", "readme.md"]:
                try:
                    readme = repo.get_contents(readme_name)
                    if readme:
                        content = base64.b64decode(readme.content).decode('utf-8')
                        readme_content = content
                        break
                except GithubException:
                    continue
            
            if not readme_content:
                return result
            
            # README exists
            result['exists'] = True
            result['length'] = len(readme_content)
            result['content'] = readme_content
            
            # Check for images
            if '![' in readme_content or '<img' in readme_content:
                result['has_images'] = True
            
            # Calculate quality score (0-5)
            quality_score = 1  # Base score for having a README
            
            # Length factor
            if len(readme_content) > 5000:
                quality_score += 1  # Comprehensive README
            elif len(readme_content) > 1500:
                quality_score += 0.5  # Decent README
            
            # Images factor
            if result['has_images']:
                quality_score += 1
            
            # Check for common documentation sections
            sections = ['installation', 'usage', 'getting started', 'api', 'examples', 'contributing']
            section_count = sum(1 for section in sections if section in readme_content.lower())
            if section_count >= 3:
                quality_score += 1
            elif section_count >= 1:
                quality_score += 0.5
            
            # Check for code examples
            if '```' in readme_content:
                quality_score += 1
            
            result['quality_score'] = min(5, quality_score)  # Cap at 5
            
            return result
        except Exception as e:
            self.logger.error(f"Error analyzing README: {str(e)}")
            return result
            
    def _get_commit_activity(self, repo: Repository) -> Dict[str, Any]:
        """
        Get commit activity for a repository.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with commit activity data
        """
        result = {
            'recent_commits': 0,
            'total_commits': 0,
            'last_commit_date': None,
            'active_development': False,
            'contributors_count': 0,
        }
        
        try:
            # Get stats contributors (this gives commit counts by contributor)
            stats_contributors = repo.get_stats_contributors()
            self.api_calls += 1
            
            if stats_contributors:
                result['contributors_count'] = len(stats_contributors)
                result['total_commits'] = sum(sc.total for sc in stats_contributors)
            
            # Get recent commits (last 30 days)
            thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
            
            # Get last commit date
            commits = repo.get_commits(since=thirty_days_ago)
            self.api_calls += 1
            
            # Count recent commits
            recent_commits = 0
            last_commit_date = None
            
            for commit in commits:
                recent_commits += 1
                if last_commit_date is None or (commit.commit.author and commit.commit.author.date > last_commit_date):
                    last_commit_date = commit.commit.author.date if commit.commit.author else None
                
                # Limit API calls
                if recent_commits >= 50:  # Only check the first 50 commits
                    break
            
            result['recent_commits'] = recent_commits
            result['last_commit_date'] = last_commit_date.isoformat() if last_commit_date else None
            
            # Consider active if there were commits in the last 14 days
            if last_commit_date:
                fourteen_days_ago = datetime.datetime.now() - datetime.timedelta(days=14)
                result['active_development'] = last_commit_date >= fourteen_days_ago
            
            return result
        except Exception as e:
            self.logger.error(f"Error getting commit activity: {str(e)}")
            return result
            
    def _get_external_website(self, repo: Repository, repo_data: Dict[str, Any]) -> Optional[str]:
        """
        Check if repository has an external website.
        
        Args:
            repo: GitHub Repository object
            repo_data: Repository data
            
        Returns:
            Website URL if found, None otherwise
        """
        # Check repository website
        if repo.homepage and repo.homepage.strip():
            url = repo.homepage.strip()
            if url.startswith('http'):
                return url
        
        # Check repository description for URLs
        if repo.description:
            url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
            matches = re.findall(url_pattern, repo.description)
            if matches:
                return matches[0]
        
        # Check README for URLs
        readme = repo_data.get('readme', {}).get('content')
        if readme:
            # Look for common website patterns in README
            patterns = [
                r'website:?\s*(https?://\S+)',
                r'site:?\s*(https?://\S+)',
                r'homepage:?\s*(https?://\S+)',
                r'\[(demo|website|homepage|live)\]\((https?://\S+)\)',
                r'<a\s+href=[\'"]?(https?://[^\'" >]+)[\'"]?\s*>\s*(?:website|homepage|demo)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, readme, re.IGNORECASE)
                if matches:
                    if isinstance(matches[0], tuple):
                        return matches[0][1]
                    else:
                        return matches[0]
        
        return None
        
    def _get_organization_data(self, org_name: str) -> Dict[str, Any]:
        """
        Get data for a GitHub organization.
        
        Args:
            org_name: Organization login name
            
        Returns:
            Dictionary with organization data
        """
        try:
            # Get organization
            org = self.github.get_organization(org_name)
            self.api_calls += 1
            
            # Extract basic organization data
            org_data = {
                'name': org.name,
                'description': org.description,
                'blog': org.blog,
                'email': org.email,
                'twitter_username': org.twitter_username,
                'public_repos': org.public_repos,
                'created_at': org.created_at.isoformat() if org.created_at else None,
                'updated_at': org.updated_at.isoformat() if org.updated_at else None,
                'has_website': bool(org.blog) and org.blog.startswith('http'),
                'total_members': 0,
                'recent_creation': False,
                'hiring_indicators': False
            }
            
            # Check if organization was created recently (last 180 days)
            if org.created_at:
                days_since_creation = (datetime.datetime.now() - org.created_at).days
                org_data['recent_creation'] = days_since_creation <= 180
            
            # Get member count
            try:
                members = list(org.get_members())
                self.api_calls += 1
                org_data['total_members'] = len(members)
            except GithubException as e:
                self.logger.warning(f"Error getting members for {org_name}: {str(e)}")
            
            # Check for hiring indicators in organization profile
            hiring_keywords = ['hiring', 'careers', 'jobs', 'join us', 'join our team', 'we\'re hiring']
            if org.description:
                if any(keyword in org.description.lower() for keyword in hiring_keywords):
                    org_data['hiring_indicators'] = True
            
            # Check for hiring indicators on website
            if org.blog and not org_data['hiring_indicators']:
                try:
                    response = rate_limited_request(self.session.get, base_delay=2.0, url=org.blog, timeout=10)
                    if response.status_code == 200:
                        content = response.text.lower()
                        if any(keyword in content for keyword in hiring_keywords):
                            org_data['hiring_indicators'] = True
                except Exception as e:
                    self.logger.warning(f"Error checking organization website: {str(e)}")
            
            return org_data
        except GithubException as e:
            self.logger.error(f"Error getting organization data for {org_name}: {str(e)}")
            return {'name': org_name, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Error processing organization {org_name}: {str(e)}")
            return {'name': org_name, 'error': str(e)}
            
    def _get_contributor_data(self, repo: Repository) -> Dict[str, Any]:
        """
        Get data about repository contributors.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with contributor metrics
        """
        try:
            contributors = list(repo.get_contributors())
            
            if repo.owner.type == 'Organization':
                # For organizations, identify external contributors
                try:
                    org_members = set(member.id for member in repo.owner.get_members())
                except GithubException:
                    # Can't access organization members, use public members
                    try:
                        org_members = set(member.id for member in repo.owner.get_public_members())
                    except GithubException:
                        org_members = set()
                        
                external_contributors = [c for c in contributors if c.id not in org_members]
                
                return {
                    'total_count': len(contributors),
                    'external_count': len(external_contributors)
                }
            else:
                # For user repositories, all contributors except the owner are external
                owner_id = repo.owner.id
                external_contributors = [c for c in contributors if c.id != owner_id]
                
                return {
                    'total_count': len(contributors),
                    'external_count': len(external_contributors)
                }
                
        except GithubException:
            # Error getting contributor data
            return {
                'total_count': 0,
                'external_count': 0
            }
            
    def _check_rate_limits(self, force: bool = False) -> bool:
        """
        Check GitHub API rate limits and wait if necessary.
        
        Args:
            force: If True, check rate limits regardless of when last checked
            
        Returns:
            True if rate limits are OK, False if exceeded
        """
        # Only check every 100 API calls unless forced
        if not force and (self.api_calls - self.last_rate_limit_check) < 100:
            return True
        
        try:
            # Get rate limits from GitHub
            rate_limit = self.github.get_rate_limit()
            self.last_rate_limit_check = self.api_calls
            
            # Check core limits
            core = rate_limit.core
            search = rate_limit.search
            
            self.logger.debug(f"GitHub API Rate Limits - Core: {core.remaining}/{core.limit}, Search: {search.remaining}/{search.limit}")
            
            # If rate limit is close to exceeded, wait until reset
            if core.remaining < 100:
                reset_time = core.reset
                if reset_time:
                    wait_seconds = (reset_time - datetime.datetime.utcnow()).total_seconds()
                    if wait_seconds > 0:
                        self.logger.warning(f"Rate limit low ({core.remaining}/{core.limit}), waiting {wait_seconds:.2f} seconds")
                        if wait_seconds > 3600:  # Don't wait more than an hour
                            return False
                        time.sleep(wait_seconds + 5)  # Add buffer
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking rate limits: {str(e)}")
            return True  # Assume OK if check fails
