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
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple

# Import modules from our project
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.utils.cache import Cache
from src.collectors.github_collector import GitHubCollector
from src.collectors.hackernews_collector import HackerNewsCollector
from src.analyzers.startup_scorer import StartupScorer
from src.analyzers.trend_analyzer import TrendAnalyzer
from src.analyzers.insights_generator import InsightsGenerator
from src.generators.report_generator import ReportGenerator
from src.generators.html_generator import HtmlGenerator
from src.generators.api_generator import ApiGenerator


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
        '--lite',
        action='store_true',
        help='Run in lite mode with minimal API calls and data collection'
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
        '--skip-hackernews',
        action='store_true',
        help='Skip Hacker News data collection'
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
        
        # Activate lite mode if specified
        if args.lite:
            logger.info("Running in lite mode with reduced API usage")
            # Limit repositories to a small number for testing
            config.set('github.max_repos_to_analyze', min(25, config.get('github.max_repos_to_analyze', 100)))
            # Skip detailed data collection in lite mode
            config.set('github.skip_detailed_analysis', True)
        
        # Set up cache
        cache = Cache()
        if args.force_refresh:
            logger.info("Forcing cache refresh")
            cache.clear()
        
        # Set up dry-run mode
        is_dry_run = args.dry_run
        if is_dry_run:
            logger.info("Running in dry-run mode - using sample data, no API calls or file writes")
        
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
                    "name": "ai-platform",
                    "full_name": "startup-org/ai-platform",
                    "url": "https://github.com/startup-org/ai-platform",
                    "description": "An AI platform for startups to automate workflows",
                    "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "language": "Python",
                    "topics": ["ai", "machine-learning", "platform", "saas", "startup"],
                    "stars": 250,
                    "forks": 45,
                    "watchers": 80,
                    "organization": "startup-org",
                    "has_website": True,
                    "has_readme": True,
                    "readme_quality": 0.85,
                    "days_since_last_commit": 2,
                    "commit_frequency": 0.8,
                    "has_tests": True,
                    "external_contributors": 5,
                    "org_data": {
                        "created_at": (datetime.now() - timedelta(days=180)).isoformat(),
                        "members_count": 6,
                        "repos_count": 4,
                        "has_website": True,
                        "description": "Building the next generation of AI tools"
                    },
                },
                {
                    "id": 67890,
                    "name": "fintech-api",
                    "full_name": "fintech-co/fintech-api",
                    "url": "https://github.com/fintech-co/fintech-api",
                    "description": "Modern API for financial technology applications",
                    "created_at": (datetime.now() - timedelta(days=60)).isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "language": "TypeScript",
                    "topics": ["fintech", "api", "financial", "payments", "blockchain"],
                    "stars": 180,
                    "forks": 30,
                    "watchers": 45,
                    "organization": "fintech-co",
                    "has_website": True,
                    "has_readme": True,
                    "readme_quality": 0.75,
                    "days_since_last_commit": 5,
                    "commit_frequency": 0.7,
                    "has_tests": True,
                    "external_contributors": 3,
                    "org_data": {
                        "created_at": (datetime.now() - timedelta(days=240)).isoformat(),
                        "members_count": 4,
                        "repos_count": 3,
                        "has_website": True,
                        "description": "Revolutionizing fintech with modern solutions"
                    }
                },
                {
                    "id": 24680,
                    "name": "saas-toolkit",
                    "full_name": "devtools/saas-toolkit",
                    "url": "https://github.com/devtools/saas-toolkit",
                    "description": "A toolkit for building modern SaaS applications",
                    "created_at": (datetime.now() - timedelta(days=45)).isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "language": "JavaScript",
                    "topics": ["saas", "toolkit", "productivity", "startup", "webapp"],
                    "stars": 120,
                    "forks": 25,
                    "watchers": 35,
                    "organization": "devtools",
                    "has_website": True,
                    "has_readme": True,
                    "readme_quality": 0.7,
                    "days_since_last_commit": 7,
                    "commit_frequency": 0.6,
                    "has_tests": True,
                    "external_contributors": 2,
                    "org_data": {
                        "created_at": (datetime.now() - timedelta(days=300)).isoformat(),
                        "members_count": 3,
                        "repos_count": 5,
                        "has_website": True,
                        "description": "Developer tools for the modern web"
                    }
                }
            ]
        
        # Step 2: Collect Hacker News discussions (if any)
        hackernews_collector = HackerNewsCollector(config, cache)
        
        if not is_dry_run and not args.skip_hackernews and not args.lite:
            logger.info("Collecting Hacker News discussions...")
            start_time = time.time()
            
            # Calculate date threshold for HN stories
            hn_days = config.get('hackernews.days_to_check', 30)
            hn_date_threshold = report_date - timedelta(days=hn_days)
            
            # Ensure date_threshold has timezone info
            if hn_date_threshold.tzinfo is None:
                hn_date_threshold = hn_date_threshold.replace(tzinfo=timezone.utc)
            
            # Collect HN discussions
            hn_discussions = hackernews_collector.collect(
                date_threshold=hn_date_threshold,
                points_threshold=config.get('hackernews.min_points', 10)
            )
            
            logger.info(f"Collected {len(hn_discussions)} Hacker News discussions in {time.time() - start_time:.2f} seconds")
        else:
            # In dry-run mode or lite mode, use sample HN data
            reason = "dry run" if is_dry_run else "lite mode" if args.lite else "hackernews collection skipped"
            logger.info(f"Using sample Hacker News data ({reason})")
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
        trends = trend_analyzer.analyze_trends(scored_repos) if scored_repos else {}
        
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
