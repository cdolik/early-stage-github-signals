#!/usr/bin/env python3
"""
Early Stage GitHub Signals Platform

This script serves as the main entry point for the platform, orchestrating the workflow of:
1. Collecting data from GitHub and Hacker News
2. Analyzing repositories to identify high-potential early-stage startups
3. Generating reports in multiple formats (Markdown, HTML, JSON API)
"""
import os
import sys
import time
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

# Add the project root directory to PYTHONPATH
# This ensures imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules from our project
from utils.config import Config
from utils.logger import setup_logger
from utils.cache import Cache
from collectors.github_collector import GitHubCollector
from collectors.hackernews_collector import HackerNewsCollector
from analyzers.startup_scorer import StartupScorer
from analyzers.trend_analyzer import TrendAnalyzer
from analyzers.insights_generator import InsightsGenerator
from generators.report_generator import ReportGenerator
from generators.html_generator import HtmlGenerator
from generators.api_generator import ApiGenerator


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Early Stage GitHub Signals Platform'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        default='config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='Enable debug logging'
    )
    parser.add_argument(
        '--force-refresh', 
        action='store_true',
        help='Force refresh of cached data'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without making API calls or writing files'
    )
    parser.add_argument(
        '--max-repos',
        type=int,
        help='Maximum number of repositories to analyze'
    )
    parser.add_argument(
        '--skip-api', 
        action='store_true',
        help='Skip API generation'
    )
    parser.add_argument(
        '--skip-html', 
        action='store_true',
        help='Skip HTML generation'
    )
    parser.add_argument(
        '--skip-reports', 
        action='store_true',
        help='Skip report generation'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Report date (YYYY-MM-DD), defaults to today'
    )
    
    return parser.parse_args()


def check_environment() -> bool:
    """
    Check if the environment is properly set up.
    
    Returns:
        True if the environment is properly set up, False otherwise
    """
    # Check for GitHub token
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        logging.error("GITHUB_TOKEN environment variable not set")
        logging.error("Please set it with: export GITHUB_TOKEN='your_token'")
        return False
        
    return True


def main() -> int:
    """Main entry point for the application."""
    args = parse_args()
    
    # Set up logging based on debug flag
    log_level = "DEBUG" if args.debug else "INFO"
    logger = setup_logger(level=log_level)
    logger.info("Starting Early Stage GitHub Signals Platform")
    
    # Check environment setup
    if not check_environment():
        logger.error("Environment check failed")
        return 1
    
    try:
        # Load configuration
        config = Config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
        
        # Override config with command-line arguments
        if args.max_repos:
            config.set('github.max_repos_to_analyze', args.max_repos)
        
        # Set up cache
        cache = Cache()
        if args.force_refresh:
            logger.info("Forcing cache refresh")
            cache.clear()
        
        # Set up dry-run mode
        is_dry_run = args.dry_run
        if is_dry_run:
            logger.info("Running in dry-run mode - no API calls or file writes")
        
        # Set report date
        if args.date:
            report_date = datetime.strptime(args.date, '%Y-%m-%d')
        else:
            report_date = datetime.now()
        
        logger.info(f"Generating report for date: {report_date.strftime('%Y-%m-%d')}")
        
        # Step 1: Collect GitHub repositories
        github_collector = GitHubCollector(config, cache)
        
        if not is_dry_run:
            logger.info("Collecting GitHub repositories...")
            start_time = time.time()
            
            # Calculate date threshold for repository creation
            trending_days = config.get('github.trending_days', 7)
            date_threshold = report_date - timedelta(days=trending_days)
            
            # Collect repositories
            repos = github_collector.collect(
                date_threshold=date_threshold,
                min_stars=config.get('github.min_stars', 5),
                max_repos=config.get('github.max_repos_to_analyze', 100)
            )
            
            logger.info(f"Collected {len(repos)} repositories in {time.time() - start_time:.2f} seconds")
        else:
            # In dry-run mode, use a small sample dataset
            logger.info("Using sample repository data for dry run")
            repos = [
                {
                    "id": 12345,
                    "name": "sample-repo",
                    "full_name": "organization/sample-repo",
                    "url": "https://github.com/organization/sample-repo",
                    "description": "A sample repository for dry run",
                    "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "language": "Python",
                    "topics": ["ai", "machine learning", "platform"],
                    "stars": 100,
                    "forks": 20,
                    "watchers": 50,
                    "organization": "organization",
                    "has_website": True,
                    "has_readme": True
                }
            ]
        
        # Step 2: Collect Hacker News discussions (if any)
        hackernews_collector = HackerNewsCollector(config, cache)
        
        if not is_dry_run:
            logger.info("Collecting Hacker News discussions...")
            start_time = time.time()
            
            # Calculate date threshold for HN stories
            hn_days = config.get('hackernews.days_to_check', 30)
            hn_date_threshold = report_date - timedelta(days=hn_days)
            
            # Collect HN discussions
            hn_discussions = hackernews_collector.collect(
                date_threshold=hn_date_threshold,
                points_threshold=config.get('hackernews.min_points', 10)
            )
            
            logger.info(f"Collected {len(hn_discussions)} Hacker News discussions in {time.time() - start_time:.2f} seconds")
        else:
            # In dry-run mode, use sample HN data
            logger.info("Using sample Hacker News data for dry run")
            hn_discussions = []
        
        # Step 3: Score repositories
        logger.info("Scoring repositories...")
        start_time = time.time()
        
        scorer = StartupScorer(config, repos, hn_discussions)
        scored_repos = []
        
        for repo in repos:
            # Find matching HN discussion if any
            hn_data = None
            for hn in hn_discussions:
                if hn.get('github_repo') == repo.get('full_name'):
                    hn_data = hn
                    break
            
            # Score repository
            scored_repo = scorer.score_repository(repo, hn_data)
            scored_repos.append(scored_repo)
        
        # Sort by score
        scored_repos = sorted(scored_repos, key=lambda r: r.get('total_score', 0), reverse=True)
        
        # Limit to top repositories
        top_repos_count = config.get('output.top_repositories_count', 25)
        if len(scored_repos) > top_repos_count:
            logger.info(f"Limiting to top {top_repos_count} repositories")
            scored_repos = scored_repos[:top_repos_count]
        
        logger.info(f"Scored {len(scored_repos)} repositories in {time.time() - start_time:.2f} seconds")
        
        # Step 4: Analyze trends
        trend_analyzer = TrendAnalyzer()
        trends = trend_analyzer.analyze_trends(scored_repos)
        
        # Calculate summary statistics for reporting
        if scored_repos:
            average_score = sum(r.get('total_score', 0) for r in scored_repos) / len(scored_repos)
            highest_score = max(r.get('total_score', 0) for r in scored_repos)
        else:
            average_score = 0
            highest_score = 0
        
        # Prepare report data
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'report_date': report_date.strftime('%Y-%m-%d'),
            'repositories': scored_repos,
            'trends': trends,
            'average_score': average_score,
            'highest_score': highest_score,
            'total_repositories': len(scored_repos)
        }
        
        # Step 5: Generate outputs
        if not is_dry_run:
            # Generate API files
            if not args.skip_api:
                logger.info("Generating API files...")
                api_generator = ApiGenerator()
                api_files = api_generator.generate(report_data)
                logger.info(f"Generated API files: {', '.join(api_files)}")
            
            # Generate HTML dashboard
            if not args.skip_html:
                logger.info("Generating HTML dashboard...")
                html_generator = HtmlGenerator()
                dashboard_path = html_generator.generate_dashboard(scored_repos, trends, report_date)
                logger.info(f"Generated HTML dashboard: {dashboard_path}")
            
            # Generate Markdown report
            if not args.skip_reports:
                logger.info("Generating Markdown report...")
                report_generator = ReportGenerator()
                report_path = report_generator.generate_report(scored_repos, trends, report_date)
                logger.info(f"Generated Markdown report: {report_path}")
        else:
            logger.info("Skipping file generation in dry-run mode")
        
        logger.info("Early Stage GitHub Signals Platform completed successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"Error running platform: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
