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
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Any

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
        '--skip-report', 
        action='store_true',
        help='Skip Markdown report generation'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run in dry-run mode (no files written)'
    )
    parser.add_argument(
        '--date', 
        type=str, 
        default=datetime.now().strftime('%Y-%m-%d'),
        help='Report date (YYYY-MM-DD)'
    )
    
    return parser.parse_args()


def check_environment() -> bool:
    """
    Check if required environment variables are set.
    Now uses Config which loads variables from .env file.
    """
    # We don't need to check for GITHUB_TOKEN here anymore as it's handled in Config
    # The Config class will try to load from .env, environment variables,
    # and fall back to config.yaml with proper warnings
    return True


def main() -> int:
    """Main entry point of the application."""
    # Parse command line arguments
    args = parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    logger = setup_logger(name=__name__, level=log_level)
    
    if not logger:  # Fallback if logger setup fails
        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
        logger = logging.getLogger(__name__)
    logger.info("Starting Early Stage GitHub Signals Platform")
    
    # Check environment
    if not check_environment():
        return 1
    
    try:
        # Load configuration
        config = Config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
        
        # Setup cache
        cache_enabled = config.get('cache.enabled', True) and not args.force_refresh
        # Temporarily modify config to apply force-refresh setting
        if not cache_enabled:
            config.set('cache.enabled', False)
            
        cache = Cache(
            config.get('cache.directory'),
            ttl=config.get('cache.ttl')
        )
        
        # Initialize collectors
        github_collector = GitHubCollector(config, cache)
        hackernews_collector = HackerNewsCollector(config, cache)
        
        # Collect repositories data
        logger.info("Collecting trending GitHub repositories")
        repositories = github_collector.collect()
        logger.info(f"Collected {len(repositories)} repositories")
        
        # Collect Hacker News data
        logger.info("Collecting Hacker News discussions")
        hn_discussions = hackernews_collector.collect()
        logger.info(f"Collected {len(hn_discussions)} Hacker News discussions")
        
        # Analyze repositories
        logger.info("Analyzing repositories for startup potential")
        scorer = StartupScorer(config, repositories, hn_discussions)
        scored_repos = scorer.score_repositories()
        logger.info(f"Scored {len(scored_repos)} repositories")
        
        # Analyze trends
        logger.info("Analyzing trends and patterns")
        trend_analyzer = TrendAnalyzer(scored_repos)
        trends = trend_analyzer.analyze()
        
        # Generate insights
        logger.info("Generating insights")
        insights_generator = InsightsGenerator(scored_repos, trends)
        insights = insights_generator.generate_insights()
        
        # Prepare data for reports
        top_count = config.get('output.top_repositories_count')
        top_repositories = sorted(
            scored_repos, 
            key=lambda x: x['total_score'], 
            reverse=True
        )[:top_count]
        
        # Add rank to repositories
        for i, repo in enumerate(top_repositories):
            repo['rank'] = i + 1
        
        report_data = {
            'repositories': top_repositories,
            'trends': trends,
            'insights': insights,
            'date': args.date,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Generate reports
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE: Verifying pipeline without writing files")
            
            # Display statistics about collected repositories
            logger.info(f"📊 Repository Statistics:")
            logger.info(f"  - Total repositories analyzed: {len(repositories)}")
            logger.info(f"  - Top {len(top_repositories)} repositories identified with startup potential")
            
            # Calculate language distribution
            languages = {}
            for repo in repositories:
                lang = repo.get('language', 'Unknown')
                if lang in languages:
                    languages[lang] += 1
                else:
                    languages[lang] = 1
            
            top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            logger.info(f"  - Top languages: {', '.join([f'{lang[0]} ({lang[1]})' for lang in top_languages])}")
            
            # Preview top repositories
            logger.info("\n🌟 Top Repository Preview:")
            for i, repo in enumerate(top_repositories[:3]):
                logger.info(f"  #{i+1}: {repo['name']} - Score: {repo['total_score']}/50")
                logger.info(f"     URL: {repo['url']}")
                logger.info(f"     Description: {repo['description'][:100] + '...' if len(repo.get('description', '')) > 100 else repo.get('description', 'No description')}")
                logger.info(f"     Key strengths: {', '.join(repo.get('insights', {}).get('strengths', ['N/A'])[:3])}")
                logger.info("")
            
            # Display trend highlights
            logger.info("📈 Trend Highlights:")
            if 'topic_distribution' in trends:
                top_topics = sorted(trends['topic_distribution'].items(), key=lambda x: x[1], reverse=True)[:5]
                logger.info(f"  - Hot topics: {', '.join([topic[0] for topic in top_topics])}")
            
            if 'language_distribution' in trends:
                logger.info(f"  - Dominant languages: {', '.join(list(trends['language_distribution'].keys())[:3])}")
                
            # Verify output directories
            report_dir = config.get('output.reports_directory', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"))
            html_dir = config.get('output.docs_directory', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs"))
            api_dir = config.get('output.api_directory', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "api"))
            
            logger.info("\n📁 Output Directory Verification:")
            
            # Check if directories exist and are writable
            for dir_path, dir_name in [(report_dir, "Report directory"), 
                                    (html_dir, "HTML directory"), 
                                    (api_dir, "API directory")]:
                if os.path.exists(dir_path):
                    if os.access(dir_path, os.W_OK):
                        logger.info(f"  ✅ {dir_name} exists and is writable: {dir_path}")
                    else:
                        logger.warning(f"  ⚠️ {dir_name} exists but is not writable: {dir_path}")
                else:
                    logger.info(f"  📝 {dir_name} will be created during actual run: {dir_path}")
            
            # Show what would be generated in actual run
            logger.info("\n📝 If run without --dry-run, would generate:")
            if not args.skip_report:
                report_filename = f"early-stage-signals-{args.date}.md"
                logger.info(f"  - Markdown report: {os.path.join(report_dir, report_filename)}")
            if not args.skip_html:
                logger.info(f"  - HTML dashboard at: {html_dir}/index.html")
            if not args.skip_api:
                logger.info(f"  - API data at: {api_dir}/latest.json and {api_dir}/{args.date}.json")
                
            logger.info("\n✅ Dry run completed successfully! All systems operational.")
            return 0
            
        if not args.skip_report:
            logger.info("Generating Markdown report")
            report_generator = ReportGenerator(config)
            report_path = report_generator.generate(report_data)
            logger.info(f"Report generated: {report_path}")
        
        if not args.skip_html:
            logger.info("Generating HTML dashboard")
            html_generator = HtmlGenerator(config)
            html_path = html_generator.generate(report_data)
            logger.info(f"HTML dashboard generated: {html_path}")
        
        if not args.skip_api:
            logger.info("Generating API data")
            api_generator = ApiGenerator(config)
            api_path = api_generator.generate(report_data)
            logger.info(f"API data generated: {api_path}")
        
        logger.info("Early Stage GitHub Signals Platform completed successfully")
        return 0
    
    except Exception as e:
        logger.exception(f"Error during execution: {str(e)}")
        return 1
