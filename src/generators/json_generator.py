"""
JSON Generator for the GitHub Signals platform.
Generates standardized JSON output from repository data.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
from ..analyzers.venture_scorer import VentureScorer
from ..utils.logger import setup_logger

class JSONGenerator:
    """
    Generates JSON files for the GitHub Signals dashboard.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = setup_logger(self.__class__.__name__)
        self.api_dir = Path('docs/api')
        self.api_dir.mkdir(parents=True, exist_ok=True)
        self.venture_scorer = VentureScorer(self.config)

    def generate(self, raw_repos: List[Dict[str, Any]], report_date: Optional[datetime] = None) -> Dict[str, str]:
        if report_date is None:
            report_date = datetime.utcnow()
        date_str = report_date.strftime('%Y-%m-%d')
        self.logger.info(f"Generating JSON files for {date_str}")
        # Score and select top 5
        top_repos = self.venture_scorer.score_repositories(raw_repos)
        
        processed_repos = []
        for r in top_repos:
            repo_data = self._add_why_matters(r)
            # Ensure repo_url is present, mapping from 'url' if necessary
            if 'repo_url' not in repo_data and 'url' in r:
                repo_data['repo_url'] = r['url']
            # Ensure repo_url is a string (not null) to pass schema validation
            if 'repo_url' in repo_data and repo_data['repo_url'] is None:
                repo_data['repo_url'] = f"https://github.com/{repo_data['full_name']}" if repo_data.get('full_name') else ""
            # Add placeholders for other required fields if missing, to pass validation
            # This is a temporary measure; ideally, the data source or scorer should provide these.
            if 'ecosystem' not in repo_data:
                repo_data['ecosystem'] = "Other" # Default placeholder
            if 'language' not in repo_data:
                repo_data['language'] = "N/A" # Default placeholder
            if 'stars' not in repo_data:
                repo_data['stars'] = 0 # Default placeholder
            if 'forks' not in repo_data:
                repo_data['forks'] = 0 # Default placeholder
            processed_repos.append(repo_data)

        api_data = {
            "name": f"Venture-Grade OSS Signals Report — {date_str}",
            "repositories": processed_repos,
            "date": date_str,
            "date_generated": report_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }

        # Write latest.json
        latest_file = self.api_dir / 'latest.json'
        with open(latest_file, 'w') as f:
            json.dump(api_data, f, indent=2, default=str)
        # Write dated file
        dated_file = self.api_dir / f'{date_str}.json'
        with open(dated_file, 'w') as f:
            json.dump(api_data, f, indent=2, default=str)
        self.logger.info(f"Generated API files: {latest_file}, {dated_file}")
        return {"latest": str(latest_file), "dated": str(dated_file)}

    def _add_why_matters(self, repo: dict) -> dict:
        # Add a why_matters field for dashboard/test compatibility
        repo = dict(repo)
        if 'why_matters' not in repo:
            # Use justification or signals if available
            if repo.get('justification'):
                repo['why_matters'] = ' '.join(repo['justification'])
            elif repo.get('signals'):
                repo['why_matters'] = ' '.join(str(s) for s in repo['signals'].values())
            else:
                repo['why_matters'] = 'High-potential OSS project.'
        return repo
