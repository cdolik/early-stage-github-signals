"""
JSON Generator for the GitHub Signals platform.
Generates standardized JSON output from repository data.
"""
import json
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional, Union

from ..utils.logger import setup_logger


class JSONGenerator:
    """
    Generates JSON files for the GitHub Signals dashboard.
    """
    
    def __init__(self, config=None):
        """
        Initialize the JSON generator.
        
        Args:
            config: Configuration manager (optional)
        """
        self.config = config
        self.logger = setup_logger("json_generator")
        self.api_dir = Path('docs/api')
        self.data_dir = Path('docs/data')
        
        # Ensure directories exist
        self.api_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, 
                 scored_repos: List[Dict[str, Any]], 
                 report_date: Optional[datetime] = None) -> Dict[str, str]:
        """
        Generate JSON files from repository data.
        
        Args:
            scored_repos: List of repositories with scores
            report_date: Report date (defaults to today)
            
        Returns:
            Dictionary with paths to the generated files
        """
        if report_date is None:
            report_date = datetime.now()
        
        date_str = report_date.strftime('%Y-%m-%d')
        self.logger.info(f"Generating JSON files for {date_str}")
        
        # Format data for API
        api_data = self._format_repos_for_api(scored_repos)
        
        # Write latest.json for API
        latest_path = self.api_dir / 'latest.json'
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2)
            
        # Write dated snapshot
        dated_path = self.data_dir / f"{date_str}.json"
        with open(dated_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2)
            
        self.logger.info(f"Generated JSON files at {latest_path} and {dated_path}")
        
        return {
            'latest': str(latest_path),
            'dated': str(dated_path)
        }
    
    def _format_repos_for_api(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format repository data for API consumption.
        
        Args:
            repos: List of repository data
            
        Returns:
            List of formatted repository data
        """
        # Sort by score descending
        sorted_repos = sorted(repos, key=lambda r: r.get('score', 0), reverse=True)
        
        formatted_repos = []
        for repo in sorted_repos:
            # Get score details
            score = repo.get('score', 0)
            score_details = repo.get('score_details', {})
            
            # Extract signals
            signals = {}
            if 'commit_surge' in score_details:
                signals['commit_surge'] = score_details['commit_surge']
            if 'star_velocity' in score_details:
                signals['star_velocity'] = score_details['star_velocity']
            if 'team_traction' in score_details:
                signals['team_traction'] = score_details['team_traction']
            if 'dev_ecosystem_fit' in score_details:
                signals['dev_ecosystem_fit'] = score_details['dev_ecosystem_fit']
            
            # Determine ecosystem category
            ecosystem = self._determine_ecosystem(repo)
            
            # Generate why_matters text
            why_matters = self._generate_why_matters_text(repo)
            
            # Format repository data
            formatted_repo = {
                "name": repo.get('name', ''),
                "full_name": repo.get('full_name', ''),
                "repo_url": repo.get('html_url', '') or repo.get('url', ''),
                "description": repo.get('description', ''),
                "score": score,
                "signals": signals,
                "ecosystem": ecosystem,
                "language": repo.get('language', ''),
                "stars": repo.get('stars', 0),
                "forks": repo.get('forks', 0),
                "why_matters": why_matters,
                "created_at": repo.get('created_at', ''),
                "topics": repo.get('topics', []),
            }
            
            # Add trend data if available
            if 'trend' in repo:
                formatted_repo['trend'] = repo['trend']
                
            formatted_repos.append(formatted_repo)
        
        return formatted_repos
    
    def _determine_ecosystem(self, repo: Dict[str, Any]) -> str:
        """
        Determine the ecosystem category for a repository.
        
        Args:
            repo: Repository data
            
        Returns:
            Ecosystem category
        """
        # Extract topics and description
        topics = [t.lower() for t in repo.get('topics', [])]
        desc = repo.get('description', '').lower()
        language = repo.get('language', '').lower()
        
        # DevOps/Infrastructure
        if any(kw in topics for kw in ['devops', 'infrastructure', 'kubernetes', 'docker']) or \
           any(kw in desc for kw in ['devops', 'infrastructure', 'kubernetes', 'docker']):
            return 'DevOps'
        
        # Frontend
        if any(kw in topics for kw in ['frontend', 'ui', 'react', 'vue', 'svelte', 'angular']) or \
           language in ['javascript', 'typescript'] or \
           any(kw in desc for kw in ['frontend', 'ui framework', 'component library']):
            return 'Frontend'
        
        # Backend
        if any(kw in topics for kw in ['backend', 'api', 'server', 'database']) or \
           language in ['go', 'rust', 'java'] or \
           any(kw in desc for kw in ['backend', 'api', 'server']):
            return 'Backend'
        
        # Data/AI
        if any(kw in topics for kw in ['ai', 'ml', 'data', 'analytics']) or \
           any(kw in desc for kw in ['machine learning', 'artificial intelligence', 'data science']):
            return 'Data/AI'
        
        # Developer Tools
        if any(kw in topics for kw in ['developer-tools', 'cli', 'sdk', 'ide']) or \
           any(kw in desc for kw in ['developer tool', 'productivity', 'cli ', 'command line']):
            return 'DevTools'
        
        # Default
        return 'Other'
    
    def _generate_why_matters_text(self, repo: Dict[str, Any]) -> str:
        """
        Generate text explaining why this repository matters.
        
        Args:
            repo: Repository data
            
        Returns:
            Explanation text
        """
        # Check if there's a manual blurb
        manual_blurb_path = Path(f"docs/manual_blurbs/{repo.get('name', '')}.md")
        if manual_blurb_path.exists():
            with open(manual_blurb_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Limit to 80 chars
                if len(content) > 80:
                    content = content[:77] + '...'
                return content
        
        # Otherwise generate from signals
        signals = repo.get('score_details', {}).get('signals', [])
        if signals:
            # Process signals to make them more concise
            processed_signals = []
            for signal in signals:
                # Remove parenthesized details
                signal = signal.split('(')[0].strip()
                # Compress common patterns
                signal = signal.replace('commits in last 14 days', 'commits')
                signal = signal.replace('stars gained in last 14 days', 'stars gained')
                signal = signal.replace('active contributors out of', 'contributors from')
                processed_signals.append(signal)
            
            # Join with bullets, limit length
            why_text = ' • '.join(processed_signals)
            if len(why_text) > 80:
                why_text = why_text[:77] + '...'
            return why_text
        
        # Fallback text
        return f"Trending {repo.get('language', '')} repository for developer tools"
