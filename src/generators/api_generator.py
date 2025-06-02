"""
API generator for GitHub repository analysis data.
"""
import os
import datetime
import json
from typing import Any, Dict, List, Optional, Tuple

from ..utils import Config, setup_logger


class ApiGenerator:
    """
    Generates JSON API files for GitHub repository analysis.
    """
    
    def __init__(self):
        """
        Initialize the API generator with configuration.
        """
        self.config = Config()
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up output directory
        self.api_dir = self.config.get(
            'output.api_directory',
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "docs", "api")
        )
        
    def generate_api(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: Optional[datetime.datetime] = None
    ) -> Tuple[str, str]:
        """
        Generate JSON API files for the analyzed repositories.
        
        Args:
            repositories: List of repositories with scores and insights
            trends: Trend analysis results
            report_date: Date for the report (defaults to today)
            
        Returns:
            Tuple of paths to the generated API files (dated, latest)
        """
        if report_date is None:
            report_date = datetime.datetime.now()
            
        date_str = report_date.strftime('%Y-%m-%d')
        
        self.logger.info(f"Generating JSON API files for {date_str}")
        
        # Prepare API data
        api_data = self._prepare_api_data(repositories, trends, report_date)
        
        # Create API directory if it doesn't exist
        os.makedirs(self.api_dir, exist_ok=True)
        
        # Write dated API file
        dated_api_path = os.path.join(self.api_dir, f"{date_str}.json")
        with open(dated_api_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2)
            
        # Write latest API file
        latest_api_path = os.path.join(self.api_dir, "latest.json")
        with open(latest_api_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2)
            
        self.logger.info(f"API files saved to {dated_api_path} and {latest_api_path}")
        return dated_api_path, latest_api_path
        
    def _prepare_api_data(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: datetime.datetime
    ) -> Dict[str, Any]:
        """
        Prepare data for the API files.
        
        Args:
            repositories: List of repositories with scores and insights
            trends: Trend analysis results
            report_date: Date for the report
            
        Returns:
            Dictionary of API data
        """
        # Sort repositories by total score
        sorted_repos = sorted(repositories, key=lambda r: r.get('total_score', 0), reverse=True)
        
        # Format repository data for the API
        api_repos = []
        for repo in sorted_repos:
            # Extract basic repository information
            api_repo = {
                'full_name': repo.get('repository', repo.get('full_name', 'Unknown')),
                'name': repo.get('name', 'Unknown'),
                'owner': repo.get('owner', {}),
                'html_url': repo.get('html_url', f"https://github.com/{repo.get('full_name', '')}"),
                'description': repo.get('description', 'No description available'),
                'language': repo.get('language', 'Unknown'),
                'stargazers_count': repo.get('stargazers_count', 0),
                'forks_count': repo.get('forks_count', 0),
                'open_issues_count': repo.get('open_issues_count', 0),
                'created_at': repo.get('created_at', ''),
                'updated_at': repo.get('updated_at', ''),
                'pushed_at': repo.get('pushed_at', ''),
                'topics': repo.get('topics', []),
                'license': repo.get('license', None),
            }
            
            # Add score information
            api_repo['scores'] = {
                'total_score': repo.get('total_score', 0),
                'repository_score': repo.get('repository_score', {}),
                'organization_score': repo.get('organization_score', {}),
                'community_score': repo.get('community_score', {}),
                'confidence_level': repo.get('confidence_level', 'low'),
            }
            
            # Add insights
            api_repo['insights'] = repo.get('insights', {})
            
            api_repos.append(api_repo)
            
        # Prepare the full API data
        return {
            'metadata': {
                'title': f"GitHub Early-Stage Startup Signals API",
                'description': "API data for GitHub repositories with high startup potential",
                'version': '1.0',
                'report_date': report_date.strftime('%Y-%m-%d'),
                'generated_at': datetime.datetime.now().isoformat(),
                'repository_count': len(repositories),
            },
            'repositories': api_repos,
            'trends': trends,
        }
