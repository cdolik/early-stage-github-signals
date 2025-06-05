"""
API generator for JSON output files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import Any, Dict, List, Optional, Tuple

from ..utils import Config, setup_logger


class ApiGenerator:
    """Generates JSON API files for the dashboard."""
    
    def __init__(self, config=None):
        """
        Initialize the API generator with configuration.
        
        Args:
            config: Configuration manager (optional)
        """
        self.config = config if config is not None else Config()
        self.logger = setup_logger(self.__class__.__name__)
        self.api_dir = Path('docs/api')
        self.api_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, report_data: dict) -> list:
        """Generate API files."""
        generated_files = []
        
        # Generate latest.json
        latest_file = self.api_dir / 'latest.json'
        api_data = self._format_api_data(report_data)
        
        with open(latest_file, 'w') as f:
            json.dump(api_data, f, indent=2, default=str)
        generated_files.append(str(latest_file))
        
        # Generate dated file
        date_str = datetime.now().strftime('%Y-%m-%d')
        dated_file = self.api_dir / f'{date_str}.json'
        
        with open(dated_file, 'w') as f:
            json.dump(api_data, f, indent=2, default=str)
        generated_files.append(str(dated_file))
        
        self.logger.info(f"Generated {len(generated_files)} API files")
        return generated_files
    
    def _format_api_data(self, report_data: dict) -> dict:
        """Format data for API consumption."""
        repositories = []
        
        for repo in report_data.get('repositories', []):
            api_repo = {
                'id': repo['id'],
                'name': repo['name'],
                'full_name': repo['full_name'],
                'url': repo['url'],
                'description': repo.get('description'),
                'language': repo.get('language'),
                'stars': repo.get('stars', 0),
                'forks': repo.get('forks', 0),
                'watchers': repo.get('watchers', 0),
                'open_issues': repo.get('open_issues', 0),
                'created_at': repo.get('created_at'),
                'updated_at': repo.get('updated_at'),
                'organization': repo.get('organization'),
                'total_score': repo.get('total_score', 0),
                'repository_score': repo.get('repository_score', 0),
                'organization_score': repo.get('organization_score', 0),
                'community_score': repo.get('community_score', 0),
                'potential_level': repo.get('potential_level'),
                'insights': repo.get('insights', {}),
                'has_website': repo.get('has_website', False),
                'topics': repo.get('topics', [])
            }
            repositories.append(api_repo)
        
        return {
            'generated_at': report_data.get('generated_at'),
            'total_repositories': len(repositories),
            'average_score': round(report_data.get('average_score', 0), 1),
            'highest_score': report_data.get('highest_score', 0),
            'repositories': repositories,
            'meta': {
                'platform': 'Early Stage GitHub Signals',
                'version': '1.0',
                'api_version': 'v1'
            }
        }
        self.api_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: Optional[datetime] = None
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
            report_date = datetime.now()
            
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
        report_date: datetime
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
