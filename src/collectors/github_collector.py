"""
GitHub data collector for the Early Stage GitHub Signals platform.
"""
import datetime
import time
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import requests
from github import Github, GithubException, RateLimitExceededException
from github.Repository import Repository
from github.Organization import Organization

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
            config: Configuration manager
            cache: Cache manager
        """
        super().__init__(config, cache)
        # Get GitHub API token from config
        self.api_token = self.config.get('github.access_token')
        if not self.api_token:
            self.logger.warning("No GitHub API token found. Rate limits will be restricted.")
            
        # Initialize the GitHub client
        self.client = Github(self.api_token)
        self.session = requests.Session()
        if self.api_token:
            self.session.headers.update({
                'Authorization': f'token {self.api_token}'
            })
        
    def get_name(self) -> str:
        """
        Get the name of the collector.
        
        Returns:
            The collector name
        """
        return "GitHub"
        
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect trending GitHub repositories based on configuration.
        
        This is the main entry point that collects repositories matching
        our criteria for startup potential.
        
        Args:
            **kwargs: Optional parameters to override config settings:
                - days: Number of days to look back (default from config)
                - min_stars: Minimum stars (default from config)
                - languages: List of languages to filter by (default from config)
                
        Returns:
            List of repository data dictionaries with all needed information
        """
        # Get parameters from kwargs or config
        days = kwargs.get('days', self.config.get('github.trending_days', 7))
        min_stars = kwargs.get('min_stars', self.config.get('github.min_stars', 5))
        languages = kwargs.get('languages', self.config.get('github.language_filter', []))
        max_repos = self.config.get('github.max_repos_to_analyze', 250)
        
        # Calculate the date threshold for "recent" repositories
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        self.logger.info(f"Collecting trending GitHub repositories created after {date_threshold.strftime('%Y-%m-%d')}")
        
        repositories = []
        
        # Collect repositories for each language
        if languages:
            for language in languages:
                self.logger.info(f"Collecting repositories for language: {language}")
                language_repos = self._collect_trending_repos(
                    language=language,
                    date_threshold=date_threshold,
                    min_stars=min_stars
                )
                repositories.extend(language_repos)
                
                # Respect rate limits
                if len(repositories) >= max_repos:
                    break
        else:
            # If no languages specified, collect general trending repos
            repositories = self._collect_trending_repos(
                date_threshold=date_threshold,
                min_stars=min_stars
            )
        
        # Limit the number of repositories to analyze
        repositories = repositories[:max_repos]
        
        # Enrich repository data with additional details
        enriched_repos = []
        for repo_data in repositories:
            try:
                # Get detailed information for scoring
                detailed_repo = self._enrich_repository_data(repo_data)
                enriched_repos.append(detailed_repo)
                # Sleep briefly to avoid hammering the API
                time.sleep(0.5)
            except Exception as e:
                self.logger.warning(f"Error enriching repository {repo_data.get('full_name')}: {str(e)}")
                enriched_repos.append(repo_data)  # Add the basic data anyway
        
        self.logger.info(f"Collected {len(enriched_repos)} repositories")
        return enriched_repos
        
    def _collect_trending_repos(
        self,
        language: Optional[str] = None,
        date_threshold: Optional[datetime.datetime] = None,
        min_stars: int = 5,
        max_repos: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Collect trending repositories with the GitHub search API.
        
        Args:
            language: Programming language filter (optional)
            date_threshold: Date threshold as datetime object
            min_stars: Minimum number of stars
            max_repos: Maximum number of repositories to collect
            
        Returns:
            List of basic repository data
        """
        # Construct the search query
        if date_threshold is None:
            date_threshold = datetime.datetime.now() - datetime.timedelta(days=7)
            
        formatted_date = date_threshold.strftime('%Y-%m-%d')
        
        query_parts = [
            f"created:>={formatted_date}",
            f"stars:>={min_stars}"
        ]
        
        if language:
            query_parts.append(f"language:{language}")
            
        query = " ".join(query_parts)
        
        try:
            # Search for repositories
            repositories = []
            page = 1
            per_page = 100  # GitHub API maximum
            
            while len(repositories) < max_repos:
                # Check rate limits
                if self._check_rate_limits():
                    # Search for repositories
                    results = self.client.search_repositories(
                        query=query,
                        sort="stars",
                        order="desc",
                        page=page,
                        per_page=per_page
                    )
                    
                    # No more results
                    if results.totalCount == 0 or page * per_page >= results.totalCount:
                        break
                        
                    # Process the results
                    for repo in results:
                        if len(repositories) >= max_repos:
                            break
                            
                        # Extract basic repository information
                        repo_data = self._extract_basic_repo_data(repo)
                        repositories.append(repo_data)
                        
                    page += 1
                    
                # If we've reached the limit, break to avoid unnecessary API calls
                if len(repositories) >= max_repos:
                    break
                    
            return repositories
            
        except RateLimitExceededException:
            self.logger.error("GitHub API rate limit exceeded. Try again later or use an API token.")
            return []
        except GithubException as e:
            self.logger.error(f"GitHub API error: {e}")
            return []
            
    def _extract_basic_repo_data(self, repo: Repository) -> Dict[str, Any]:
        """
        Extract basic data from a GitHub Repository object.
        
        Args:
            repo: The GitHub Repository object
            
        Returns:
            Dictionary with basic repository data
        """
        return {
            'id': repo.id,
            'full_name': repo.full_name,
            'name': repo.name,
            'owner': {
                'login': repo.owner.login,
                'type': repo.owner.type,
                'id': repo.owner.id,
                'url': repo.owner.html_url,
            },
            'html_url': repo.html_url,
            'description': repo.description,
            'created_at': repo.created_at.isoformat(),
            'updated_at': repo.updated_at.isoformat(),
            'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
            'language': repo.language,
            'stargazers_count': repo.stargazers_count,
            'watchers_count': repo.watchers_count,
            'forks_count': repo.forks_count,
            'open_issues_count': repo.open_issues_count,
            'topics': repo.topics,
            'has_wiki': repo.has_wiki,
            'has_pages': repo.has_pages,
            'has_projects': repo.has_projects,
            'has_downloads': repo.has_downloads,
            'license': repo.license.name if repo.license else None,
            'default_branch': repo.default_branch,
        }
        
    def _enrich_repository_data(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich repository data with additional information.
        
        Args:
            repo_data: Basic repository data dictionary
            
        Returns:
            Enriched repository data dictionary
        """
        self.logger.debug(f"Enriching data for repository: {repo_data['full_name']}")
        
        # Try to get data from cache first
        cache_key = f"repo_{repo_data['id']}_details"
        cached_data = self.cache.get(cache_key) if self.cache else None
        
        if cached_data:
            self.logger.debug(f"Found cached data for {repo_data['full_name']}")
            return cached_data
        
        try:
            # Get the full repository object
            repo = self.client.get_repo(repo_data['full_name'])
            
            # Check rate limits before making additional API calls
            if not self._check_rate_limits():
                # Return the basic data without enrichment
                return repo_data
            
            # Enrich with additional data
            enriched_data = repo_data.copy()
            
            # Check for CI/CD setup
            enriched_data['ci_cd_setup'] = self._has_ci_cd_setup(repo)
            
            # Check for tests
            enriched_data['has_tests'] = self._has_tests(repo)
            
            # Get readme quality
            enriched_data['readme_quality'] = self._get_readme_quality(repo)
            
            # Get recent commit activity
            enriched_data['commit_activity'] = self._get_commit_activity(repo)
            
            # Get external website
            enriched_data['external_website'] = self._get_external_website(repo, repo_data)
            
            # Get organization data if applicable
            if repo_data['owner']['type'] == 'Organization':
                enriched_data['organization'] = self._get_organization_data(repo.owner.login)
            else:
                enriched_data['organization'] = None
            
            # Get contributor data
            enriched_data['contributors'] = self._get_contributor_data(repo)
                
            # Get repository details
            repo_details = self.get_repository_details(repo)
            if repo_details:
                enriched_data.update(repo_details)
                
            # Cache the enriched data
            if self.cache:
                self.cache.set(cache_key, enriched_data, expire=86400)  # Cache for 24 hours
                
            return enriched_data
            
        except RateLimitExceededException:
            self.logger.warning(f"GitHub API rate limit exceeded during enrichment of {repo_data['full_name']}")
            return repo_data
        except GithubException as e:
            self.logger.warning(f"GitHub API error during enrichment of {repo_data['full_name']}: {e}")
            return repo_data
        except Exception as e:
            self.logger.error(f"Error enriching data for {repo_data['full_name']}: {e}")
            return repo_data
            
    def get_repository_details(self, repo: Repository) -> Dict[str, Any]:
        """
        Get detailed information about a repository.

        Args:
            repo: GitHub Repository object

        Returns:
            Dictionary with detailed repository information
        """
        try:
            # Extract additional details
            details = {
                'watchers_count': repo.watchers_count,
                'network_count': repo.network_count,
                'subscribers_count': repo.subscribers_count,
                'is_fork': repo.fork,
                'parent': repo.parent.full_name if repo.fork and repo.parent else None,
                'source': repo.source.full_name if repo.source else None,
                'has_issues': repo.has_issues,
                'has_projects': repo.has_projects,
                'has_downloads': repo.has_downloads,
                'has_wiki': repo.has_wiki,
                'has_pages': repo.has_pages,
                'archived': repo.archived,
                'disabled': repo.disabled,
                'visibility': repo.visibility,
            }

            return details
        except GithubException as e:
            self.logger.warning(f"Error fetching repository details for {repo.full_name}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error fetching repository details for {repo.full_name}: {e}")
            return {}
    
        
    def _has_ci_cd_setup(self, repo: Repository) -> bool:
        """
        Check if a repository has CI/CD setup.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            True if CI/CD setup found, False otherwise
        """
        # Check for common CI/CD configuration files
        ci_files = [
            '.github/workflows',
            '.travis.yml',
            'circle.yml', '.circleci/config.yml',
            'Jenkinsfile',
            '.gitlab-ci.yml',
            'azure-pipelines.yml',
            '.drone.yml',
            'appveyor.yml',
            '.github/actions'
        ]
        
        try:
            for file_path in ci_files:
                try:
                    # Try to get the content of the file or directory listing
                    repo.get_contents(file_path)
                    # If no exception, file exists
                    return True
                except GithubException:
                    # File does not exist, try next
                    continue
            
            # No CI/CD files found
            return False
        except GithubException:
            # Error accessing repository contents
            return False
            
    def _has_tests(self, repo: Repository) -> bool:
        """
        Check if a repository has test files.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            True if tests found, False otherwise
        """
        # Check for common test directories and files
        test_paths = [
            'test', 'tests', 'Test', 'Tests',
            'spec', 'specs', 'Spec', 'Specs',
            '__tests__', '__test__',
            'test.py', 'test.js', 'test.ts', 'test.go',
            'test.java', 'test.rb', 'test.php'
        ]
        
        try:
            # Get top level contents
            contents = repo.get_contents("")
            
            for content in contents:
                if content.type == "dir" and content.name.lower() in [p.lower() for p in test_paths]:
                    return True
                elif content.name.lower() in [p.lower() for p in test_paths]:
                    return True
            
            # Check if there are files with "test" in the name
            search_url = f"https://api.github.com/search/code?q=test+in:path+repo:{repo.full_name}"
            response = rate_limited_request(
                self.session.get,
                url=search_url,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('total_count', 0) > 0:
                    return True
            
            return False
        except GithubException:
            # Error accessing repository contents
            return False
            
    def _get_readme_quality(self, repo: Repository) -> Dict[str, Any]:
        """
        Analyze the quality of the repository README.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with readme quality metrics
        """
        try:
            try:
                readme = repo.get_readme()
                content = readme.decoded_content.decode('utf-8')
                
                # Calculate readme metrics
                length = len(content)
                has_images = '![' in content or '<img' in content
                has_headings = '#' in content or '<h1' in content or '<h2' in content
                has_code = '```' in content or '`' in content or '<code' in content
                has_links = '(' in content or 'http' in content or '<a href' in content
                sections = content.count('#') + content.count('<h')
                
                # Score the readme (simple heuristic)
                score = 0
                if length > 500:  # Good length
                    score += 0.5
                if length > 1000:  # Comprehensive
                    score += 0.5
                if has_images:  # Visual aids
                    score += 0.25
                if has_headings:  # Organized
                    score += 0.25
                if has_code:  # Code examples
                    score += 0.25
                if has_links:  # References
                    score += 0.25
                if sections > 3:  # Multiple sections
                    score += 0.5
                    
                return {
                    'exists': True,
                    'length': length,
                    'has_images': has_images,
                    'has_headings': has_headings,
                    'has_code': has_code,
                    'has_links': has_links,
                    'sections': sections,
                    'score': min(score, 2.0)  # Scale to 2.0 max
                }
                
            except GithubException:
                # No README found
                return {
                    'exists': False,
                    'length': 0,
                    'has_images': False,
                    'has_headings': False,
                    'has_code': False,
                    'has_links': False,
                    'sections': 0,
                    'score': 0.0
                }
        except Exception:
            # Error analyzing README
            return {
                'exists': False,
                'length': 0,
                'has_images': False,
                'has_headings': False,
                'has_code': False,
                'has_links': False,
                'sections': 0,
                'score': 0.0
            }
            
    def _get_commit_activity(self, repo: Repository) -> Dict[str, Any]:
        """
        Get the commit activity for a repository.
        
        Args:
            repo: GitHub Repository object
            
        Returns:
            Dictionary with commit activity metrics
        """
        try:
            # Get commits from the last week
            commits = repo.get_commits(since=datetime.datetime.now() - datetime.timedelta(days=7))
            commit_count = 0
            authors = set()
            
            for commit in commits:
                commit_count += 1
                if commit.author:
                    authors.add(commit.author.login)
                    
            return {
                'weekly_commits': commit_count,
                'unique_authors': len(authors)
            }
        except GithubException:
            # Error getting commit activity
            return {
                'weekly_commits': 0,
                'unique_authors': 0
            }
            
    def _get_external_website(self, repo: Repository, repo_data: Dict[str, Any]) -> Optional[str]:
        """
        Get the external website URL for a repository.
        
        Args:
            repo: GitHub Repository object
            repo_data: Repository data dictionary
            
        Returns:
            Website URL if available, None otherwise
        """
        # Check if website is set in repository info
        if repo.homepage and repo.homepage.strip() and repo.homepage.startswith(('http://', 'https://')):
            return repo.homepage.strip()
            
        # Check repository description for URLs
        if repo_data['description']:
            import re
            urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', repo_data['description'])
            if urls:
                return urls[0]
                
        return None
        
    def _get_organization_data(self, org_name: str) -> Dict[str, Any]:
        """
        Get data about a GitHub organization.
        
        Args:
            org_name: Organization login name
            
        Returns:
            Dictionary with organization data
        """
        try:
            org = self.client.get_organization(org_name)
            
            # Get basic organization data
            org_data = {
                'login': org.login,
                'name': org.name,
                'blog': org.blog,
                'email': org.email,
                'bio': org.bio,
                'location': org.location,
                'public_repos': org.public_repos,
                'followers': org.followers,
                'created_at': org.created_at.isoformat() if org.created_at else None,
                'updated_at': org.updated_at.isoformat() if org.updated_at else None,
                'has_website': bool(org.blog),
            }
            
            # Check for hiring indicators in organization bio or description
            hiring_keywords = ['hiring', 'careers', 'jobs', 'join us', 'join our team',
                             'we\'re hiring', 'open positions', 'apply', 'vacancy']
            
            has_hiring = False
            if org.bio:
                has_hiring = any(keyword in org.bio.lower() for keyword in hiring_keywords)
                
            org_data['hiring_indicators'] = has_hiring
            
            # Get team size (member count)
            try:
                members = list(org.get_members())
                org_data['team_size'] = len(members)
            except GithubException:
                # Can't access members, use public members as fallback
                try:
                    public_members = list(org.get_public_members())
                    org_data['team_size'] = len(public_members)
                except GithubException:
                    org_data['team_size'] = 0
                    
            return org_data
            
        except GithubException:
            # Error getting organization data
            return {
                'login': org_name,
                'name': None,
                'blog': None,
                'email': None,
                'bio': None,
                'location': None,
                'public_repos': 0,
                'followers': 0,
                'created_at': None,
                'updated_at': None,
                'has_website': False,
                'hiring_indicators': False,
                'team_size': 0
            }
            
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
            
    def _check_rate_limits(self) -> bool:
        """
        Check GitHub API rate limits and wait if necessary.
        
        Returns:
            True if rate limit is OK, False if waiting for reset
        """
        try:
            # Get rate limit information
            rate_limit = self.client.get_rate_limit()
            core_limit = rate_limit.core
            search_limit = rate_limit.search
            
            # Check core rate limit
            if core_limit.remaining < 10:  # Keep some buffer
                reset_time = core_limit.reset.timestamp()
                wait_time = max(1, reset_time - time.time())
                
                self.logger.warning(f"GitHub core API rate limit approaching. "
                                  f"Waiting {wait_time:.1f} seconds for reset.")
                                  
                if wait_time > 60:  # If wait time is long, return False
                    return False
                    
                time.sleep(wait_time)
                
            # Check search rate limit if very low
            if search_limit.remaining < 3:
                reset_time = search_limit.reset.timestamp()
                wait_time = max(1, reset_time - time.time())
                
                self.logger.warning(f"GitHub search API rate limit approaching. "
                                  f"Waiting {wait_time:.1f} seconds for reset.")
                                  
                if wait_time > 60:  # If wait time is long, return False
                    return False
                    
                time.sleep(wait_time)
                
            return True
            
        except GithubException:
            # Error checking rate limit
            return True  # Assume it's OK and let the API calls handle any errors
