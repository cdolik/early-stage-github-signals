"""
Weekly dev tools gems report generator.
Produces the weekly report based on the updated scoring system.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any

from ..utils.logger import setup_logger


class WeeklyGemsReportGenerator:
    """
    Generator for Weekly Dev Tools Gems report.
    """
    
    def __init__(self, config=None):
        """
        Initialize the report generator.
        
        Args:
            config: Configuration manager (optional)
        """
        self.config = config
        self.logger = setup_logger("weekly_gems")
        self.quality_threshold = 7  # Minimum score to be included
        
    def generate_report(self, scored_repos: List[Dict[str, Any]], report_date: datetime = None) -> str:
        """
        Generate the Weekly Dev Tools Gems report.
        
        Args:
            scored_repos: List of repositories with scores and signals
            report_date: Report date (defaults to today)
            
        Returns:
            Path to the generated report file
        """
        if report_date is None:
            report_date = datetime.now()
            
        date_str = report_date.strftime('%Y-%m-%d')
        
        self.logger.info(f"Generating Weekly Dev Tools Gems report for {date_str}")
        
        # Filter for repos that meet quality threshold
        quality_repos = [r for r in scored_repos if r.get('score', 0) >= self.quality_threshold]
        
        # Sort by score (highest first)
        quality_repos = sorted(quality_repos, key=lambda r: r.get('score', 0), reverse=True)
        
        # Generate the markdown report
        report_content = self._generate_markdown(quality_repos, date_str)
        
        # Save the report
        reports_dir = os.path.join(os.getcwd(), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        report_file = os.path.join(reports_dir, f'weekly_gems_{date_str}.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"Report saved to {report_file}")
        
        # Also save as latest
        latest_file = os.path.join(reports_dir, 'weekly_gems_latest.md')
        with open(latest_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        # Save JSON data for API access
        json_file = os.path.join(reports_dir, f'weekly_gems_{date_str}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': date_str,
                'repos': quality_repos,
                'threshold': self.quality_threshold
            }, f, indent=2)
            
        return report_file
        
    def _generate_markdown(self, repos: List[Dict[str, Any]], date_str: str) -> str:
        """Generate the markdown report content."""
        lines = [
            f"# Weekly Dev Tools Gems - {date_str}",
            "*USA-focused, GitHub ecosystem, seed-stage*\n",
            f"*Quality threshold: {self.quality_threshold}+/10 points*\n"
        ]
        
        if not repos:
            lines.append("**No discoveries met quality threshold this week.**")
            lines.append("\nOur strict quality criteria ensures we only highlight repos with genuine momentum.")
            return "\n".join(lines)
            
        # Add each repository
        for i, repo in enumerate(repos, 1):
            name = repo.get('name', '')
            full_name = repo.get('full_name', '')
            url = repo.get('html_url', '') or repo.get('url', '')
            score = repo.get('score', 0)
            
            # Format signals
            signals = []
            details = repo.get('score_details', {})
            
            if details.get('commit_surge', 0) > 0 and 'commits' in str(details.get('signals', [])):
                for signal in details.get('signals', []):
                    if 'commits' in signal:
                        signals.append(signal)
                        break
                        
            if details.get('star_velocity', 0) > 0 and 'stars' in str(details.get('signals', [])):
                for signal in details.get('signals', []):
                    if 'stars' in signal:
                        signals.append(signal)
                        break
                        
            if details.get('team_traction', 0) > 0 and 'contributors' in str(details.get('signals', [])):
                for signal in details.get('signals', []):
                    if 'contributors' in signal:
                        signals.append(signal)
                        break
                        
            signals_text = ', '.join(signals)
            
            # Get VC Hook if available
            vc_hook = repo.get('vc_hook', '')
            if not vc_hook and repo.get('description'):
                # If no VC hook provided, use the description
                vc_hook = repo.get('description')
                
            # Add to report
            lines.append(f"{i}. **[{full_name}]({url})** - {score}/10 points")
            lines.append(f"   - Signals: {signals_text}")
            if vc_hook:
                lines.append(f"   - VC Hook: {vc_hook}")
            lines.append("")
            
        return "\n".join(lines)
