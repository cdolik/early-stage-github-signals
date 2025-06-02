"""
Markdown report generator for GitHub repository analysis.
"""
import os
import datetime
import json
from typing import Any, Dict, List, Optional, Tuple

import jinja2

from ..utils import Config, setup_logger, sanitize_filename


class ReportGenerator:
    """
    Generates Markdown reports for GitHub repository analysis.
    """
    
    def __init__(self):
        """
        Initialize the report generator with configuration.
        """
        self.config = Config()
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up Jinja2 template environment
        self.template_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "templates",
            "markdown"
        )
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Set up output directory
        self.reports_dir = self.config.get(
            'output.reports_directory',
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "reports")
        )
        
    def generate_report(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: Optional[datetime.datetime] = None
    ) -> str:
        """
        Generate a markdown report for the analyzed repositories.
        
        Args:
            repositories: List of repositories with scores and insights
            trends: Trend analysis results
            report_date: Date for the report (defaults to today)
            
        Returns:
            Path to the generated report
        """
        if report_date is None:
            report_date = datetime.datetime.now()
            
        date_str = report_date.strftime('%Y-%m-%d')
        
        self.logger.info(f"Generating markdown report for {date_str}")
        
        # Prepare report data
        report_data = self._prepare_report_data(repositories, trends, report_date)
        
        # Load and render the template
        try:
            template = self.env.get_template("weekly_report.md")
            report_content = template.render(**report_data)
        except jinja2.exceptions.TemplateNotFound:
            self.logger.warning("Template not found. Using default template.")
            report_content = self._generate_default_report(report_data)
        except Exception as e:
            self.logger.error(f"Error rendering template: {e}")
            report_content = self._generate_default_report(report_data)
            
        # Create the report directory
        report_dir = os.path.join(self.reports_dir, date_str)
        os.makedirs(report_dir, exist_ok=True)
        
        # Write the report to file
        report_path = os.path.join(report_dir, "README.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        self.logger.info(f"Report saved to {report_path}")
        return report_path
        
    def _prepare_report_data(
        self,
        repositories: List[Dict[str, Any]],
        trends: Dict[str, Any],
        report_date: datetime.datetime
    ) -> Dict[str, Any]:
        """
        Prepare data for the report template.
        
        Args:
            repositories: List of repositories with scores and insights
            trends: Trend analysis results
            report_date: Date for the report
            
        Returns:
            Dictionary of data for the template
        """
        # Sort repositories by total score
        sorted_repos = sorted(repositories, key=lambda r: r.get('total_score', 0), reverse=True)
        
        # Get top repositories
        top_count = self.config.get('output.top_repositories_count', 25)
        top_repositories = sorted_repos[:top_count]
        
        # Format the repository data for the report
        repo_table_data = []
        for repo in top_repositories:
            repo_data = repo.copy()
            
            # Basic repository info
            repo_info = {
                'full_name': repo.get('repository', repo.get('full_name', 'Unknown')),
                'url': repo.get('html_url', f"https://github.com/{repo.get('full_name', '')}"),
                'description': repo.get('description', 'No description available'),
                'language': repo.get('language', 'Unknown'),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'age_days': None,
            }
            
            # Calculate repository age
            created_at = repo.get('created_at')
            if created_at:
                try:
                    created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.datetime.now().replace(tzinfo=None) - 
                              created_date.replace(tzinfo=None)).days
                    repo_info['age_days'] = age_days
                except (ValueError, TypeError):
                    pass
                    
            # Score information
            score_info = {
                'total_score': repo.get('total_score', 0),
                'repo_score': repo.get('repository_score', {}).get('total', 0),
                'org_score': repo.get('organization_score', {}).get('total', 0),
                'community_score': repo.get('community_score', {}).get('total', 0),
                'confidence': repo.get('confidence_level', 'low'),
            }
            
            # Insights
            insights = repo.get('insights', {})
            insights_info = {
                'summary': insights.get('summary', ''),
                'strengths': insights.get('strengths', [])[:3],  # Top 3 strengths
                'product': insights.get('potential_product', ''),
            }
            
            # Combine the data
            table_entry = {**repo_info, **score_info, **{'insights': insights_info}}
            repo_table_data.append(table_entry)
            
        # Prepare the full report data
        return {
            'title': f"Weekly GitHub Startup Signals Report: {report_date.strftime('%B %d, %Y')}",
            'date': report_date.strftime('%Y-%m-%d'),
            'repositories': repo_table_data,
            'repository_count': len(repositories),
            'trends': trends,
            'dashboard_url': '../docs/index.html',
            'api_url': f'../docs/api/{report_date.strftime("%Y-%m-%d")}.json',
        }
        
    def _generate_default_report(self, data: Dict[str, Any]) -> str:
        """
        Generate a default report if template rendering fails.
        
        Args:
            data: Report data
            
        Returns:
            Markdown report content
        """
        date = data.get('date', datetime.datetime.now().strftime('%Y-%m-%d'))
        repos = data.get('repositories', [])
        
        # Build the report manually
        lines = [
            f"# Weekly GitHub Startup Signals Report: {date}",
            "",
            f"This report analyzes {data.get('repository_count', 0)} GitHub repositories for startup potential.",
            "",
            "## Top Repositories",
            "",
            "| Repository | Score | Confidence | Language | Stars | Age | Summary |",
            "| ---------- | ----- | ---------- | -------- | ----- | --- | ------- |"
        ]
        
        # Add repository rows
        for repo in repos:
            name = repo.get('full_name', 'Unknown')
            url = repo.get('url', '#')
            score = repo.get('total_score', 0)
            confidence = repo.get('confidence', 'low')
            language = repo.get('language', 'Unknown')
            stars = repo.get('stars', 0)
            age = repo.get('age_days', 'Unknown')
            summary = repo.get('insights', {}).get('summary', 'No summary available')
            
            # Format row
            lines.append(
                f"| [{name}]({url}) | {score:.1f} | {confidence.title()} | {language} | {stars} | {age} | {summary[:100]}... |"
            )
            
        # Add trends section if available
        if 'trends' in data:
            trends = data.get('trends', {})
            
            lines.extend([
                "",
                "## Trends",
                "",
                "### Languages",
                ""
            ])
            
            # Add language distribution
            languages = trends.get('language_distribution', {}).get('top_languages', [])
            if languages:
                lines.append("Top languages:")
                for lang, count in languages:
                    lines.append(f"- {lang}: {count} repositories")
                    
            # Add more trend sections as needed
            
        # Add footer
        lines.extend([
            "",
            "## About this Report",
            "",
            "This report was generated automatically using the GitHub Signals platform.",
            f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}.",
            "",
            "[View Interactive Dashboard](../docs/index.html)",
            "",
        ])
        
        return "\n".join(lines)
