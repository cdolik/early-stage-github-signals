#!/usr/bin/env python3
"""
Weekly Dev Tools Gems CLI - Simple MVP implementation
Collects data from GitHub Trending, Product Hunt, and Hacker News,
scores repositories using the 10-point momentum system,
and generates a weekly report.
"""
import argparse
import os
import sys
import datetime
import logging
from github import Github
from typing import Dict, List, Any
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.collectors.trending_collector import TrendingCollector
from src.collectors.producthunt_collector import ProductHuntCollector
from src.collectors.showhn_collector import ShowHNCollector
from src.analyzers.momentum_scorer import MomentumScorer
from src.generators.weekly_gems_generator import WeeklyGemsReportGenerator
from src.generators.json_generator import JSONGenerator
from src.utils.logger import setup_logger
from src.utils.config import Config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Weekly Dev Tools Gems CLI')
    parser.add_argument('--config', type=str, default='config.yaml', help='Path to config file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--max-repos', type=int, default=25, help='Maximum repositories to process')
    parser.add_argument('--min-stars', type=int, default=5, help='Minimum stars for consideration')
    parser.add_argument('--skip-producthunt', action='store_true', help='Skip Product Hunt collection')
    parser.add_argument('--skip-hackernews', action='store_true', help='Skip Hacker News collection')
    parser.add_argument('--skip-api', action='store_true', help='Skip API file generation')
    return parser.parse_args()


def generate_api_json(scored_repos: List[Dict[str, Any]], report_date: datetime.datetime) -> Dict[str, str]:
    """
    Generate JSON API files for the dashboard based on the 10-point system.
    
    Args:
        scored_repos: List of repositories with scores
        report_date: Date of the report
        
    Returns:
        Dictionary with paths to the generated files
    """
    # Use the new JSONGenerator to generate all files
    json_generator = JSONGenerator()
    generated_files = json_generator.generate(scored_repos, report_date)
    
    return generated_files


def main():
    """Main entry point for the CLI."""
    # Parse arguments
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(level=log_level)
    logger.info("Starting Weekly Dev Tools Gems CLI")
    
    # Load configuration
    config = Config(args.config)
    
    # Initialize GitHub API client if token available
    github_token = os.environ.get('GITHUB_TOKEN')
    github_client = None
    if github_token:
        github_client = Github(github_token)
        logger.info("GitHub API client initialized")
    else:
        logger.warning("GITHUB_TOKEN not found - some scoring features will be limited")
    
    # Step 1: Collect data from sources
    all_repos = []
    
    # Collect from GitHub Trending
    logger.info("Collecting from GitHub Trending")
    trending_collector = TrendingCollector(config)
    trending_repos = trending_collector.collect(
        timespan='weekly',
        max_repos=args.max_repos
    )
    logger.info(f"Collected {len(trending_repos)} trending repositories")
    all_repos.extend(trending_repos)
    
    # Collect from Product Hunt (if not skipped)
    if not args.skip_producthunt:
        logger.info("Collecting from Product Hunt")
        ph_collector = ProductHuntCollector(config)
        ph_products = ph_collector.collect(
            min_upvotes=50,
            max_products=args.max_repos
        )
        
        # Try to match with GitHub repositories
        ph_repos = []
        for product in ph_products:
            repo_name = ph_collector.match_with_github_repo(product)
            if repo_name:
                # Found a GitHub repo match
                # In a real implementation, we would fetch repo details
                # For MVP, we'll create a simple placeholder with the data we have
                ph_repos.append({
                    'full_name': repo_name,
                    'name': repo_name.split('/')[-1] if '/' in repo_name else repo_name,
                    'html_url': f"https://github.com/{repo_name}",
                    'description': product.get('tagline', ''),
                    'ph_url': product.get('ph_url', ''),
                    'ph_upvotes': product.get('upvotes', 0),
                    'source': 'product_hunt'
                })
        
        logger.info(f"Matched {len(ph_repos)} Product Hunt products with GitHub repos")
        all_repos.extend(ph_repos)
    
    # Collect from Hacker News (if not skipped)
    if not args.skip_hackernews:
        logger.info("Collecting from Hacker News")
        hn_collector = ShowHNCollector(config)
        hn_stories = hn_collector.collect(
            min_points=50,
            max_posts=args.max_repos,
            days_back=7
        )
        
        # Try to match with GitHub repositories
        hn_repos = []
        for story in hn_stories:
            repo_name = hn_collector.match_with_github_repo(story)
            if repo_name:
                # Found a GitHub repo match
                hn_repos.append({
                    'full_name': repo_name,
                    'name': repo_name.split('/')[-1] if '/' in repo_name else repo_name,
                    'html_url': f"https://github.com/{repo_name}",
                    'description': story.get('title', ''),
                    'hn_url': story.get('hn_url', ''),
                    'hn_points': story.get('points', 0),
                    'source': 'hacker_news'
                })
        
        logger.info(f"Matched {len(hn_repos)} Hacker News stories with GitHub repos")
        all_repos.extend(hn_repos)
    
    # Deduplicate repositories by full_name
    unique_repos = {}
    for repo in all_repos:
        full_name = repo.get('full_name')
        if full_name and full_name not in unique_repos:
            unique_repos[full_name] = repo
        elif full_name in unique_repos:
            # Merge data from multiple sources
            unique_repos[full_name].update({k: v for k, v in repo.items() 
                                          if k not in unique_repos[full_name]})
    
    all_repos = list(unique_repos.values())
    logger.info(f"Total unique repositories: {len(all_repos)}")
    
    # Step 2: Score repositories
    logger.info("Scoring repositories")
    momentum_scorer = MomentumScorer(config, github_client, logger)
    
    scored_repos = []
    for repo in all_repos:
        try:
            score, details = momentum_scorer.score_repository(repo)
            repo_with_score = {**repo, 'score': score, 'score_details': details}
            scored_repos.append(repo_with_score)
            logger.debug(f"Scored {repo.get('full_name', 'unknown')} with {score}/10")
        except Exception as e:
            logger.error(f"Error scoring {repo.get('full_name', 'unknown')}: {str(e)}")
    
    # Step 3: Generate report
    logger.info("Generating weekly report")
    report_generator = WeeklyGemsReportGenerator(config)
    report_path = report_generator.generate_report(scored_repos)
    
    # Step 4: Generate API JSON (if not skipped)
    if not args.skip_api:
        logger.info("Generating API JSON for dashboard")
        generated_files = generate_api_json(scored_repos, datetime.datetime.now())
        logger.info(f"API JSON files generated: {', '.join(generated_files.values())}")
    
    logger.info(f"Weekly Dev Tools Gems report generated: {report_path}")
    print(f"\nReport generated: {report_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
