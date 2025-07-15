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

# Add dotenv loading with robust path detection
try:
    from dotenv import load_dotenv

    # Look for .env file in multiple locations
    env_paths = [
        # Current directory
        Path(".env"),
        # Project root directory
        Path(__file__).parent / ".env",
        # Home directory (fallback)
        Path.home() / ".early-stage-github-signals" / ".env",
    ]

    dotenv_loaded = False
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            dotenv_loaded = True
            print(f"Loaded environment variables from {env_path}")
            break

    if not dotenv_loaded:
        # Try the default load_dotenv behavior as last resort
        dotenv_loaded = load_dotenv()
        if dotenv_loaded:
            print("Loaded environment variables using default path")
        else:
            print("Warning: No .env file found. GitHub API features may be limited.")
            print(
                "Tip: Run 'make setup' or copy .env.example to .env and add your GitHub token"
            )
except ImportError:
    print(
        "Warning: python-dotenv not installed. Installing dependencies with 'pip install -r requirements.txt' is recommended."
    )


# Debug function to check environment variables
def debug_env_vars():
    """Print environment variables for debugging."""
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        preview = github_token[:4] + "..." if len(github_token) > 4 else "[empty]"
        print(f"DEBUG: GITHUB_TOKEN is set (starts with: {preview})")
    else:
        print("DEBUG: GITHUB_TOKEN is not set")

    # Print the current working directory
    print(f"DEBUG: Current working directory: {os.getcwd()}")

    # Check if .env file exists
    env_file = Path(".env")
    print(f"DEBUG: .env file in current directory exists: {env_file.exists()}")
    
    # Check project root .env
    project_env = Path(__file__).parent / ".env"
    print(f"DEBUG: .env file at {project_env} exists: {project_env.exists()}")


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
    parser = argparse.ArgumentParser(
        description="Early Stage GitHub Signals - Weekly Dev Tools Gems CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config", type=str, default="config.yaml", help="Path to configuration file"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--max-repos", type=int, default=25, help="Maximum repositories to process"
    )
    parser.add_argument(
        "--min-stars", type=int, default=5, help="Minimum stars for consideration"
    )
    parser.add_argument(
        "--skip-producthunt", action="store_true", help="Skip Product Hunt collection"
    )
    parser.add_argument(
        "--skip-hackernews", action="store_true", help="Skip Hacker News collection"
    )
    parser.add_argument(
        "--skip-api", action="store_true", help="Skip API file generation"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip cache and force refresh from all sources",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        help="Override quality threshold score (default from config)",
    )
    parser.add_argument(
        "--github-token",
        type=str,
        help="GitHub Personal Access Token (overrides GITHUB_TOKEN env var)",
    )
    parser.add_argument(
        "--verify-token", action="store_true", help="Verify GitHub token and exit"
    )
    return parser.parse_args()


def generate_api_json(
    scored_repos: List[Dict[str, Any]], report_date: datetime.datetime
) -> Dict[str, str]:
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


def validate_github_token(token):
    """
    Validate GitHub token by making a simple API request.

    Args:
        token: GitHub token to validate

    Returns:
        Tuple of (is_valid, message)
    """
    if not token:
        return False, "Token is empty or None"

    try:
        g = Github(token)
        # First check rate limit to see if token works
        rate_limit = g.get_rate_limit()
        remaining_calls = rate_limit.core.remaining

        # Then get user info
        user = g.get_user()
        username = user.login

        return (
            True,
            f"Token valid for user: {username} (Rate limit: {remaining_calls} API calls remaining)",
        )
    except Exception as e:
        error_message = str(e)
        # Don't include the token in error messages
        sanitized_error = (
            error_message.replace(token, "[TOKEN]")
            if token in error_message
            else error_message
        )
        return False, f"Token validation failed: {sanitized_error}"


def validate_data(scored_repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate repository data and ensure it's complete before generating output.

    Args:
        scored_repos: List of scored repositories

    Returns:
        List of validated repositories with missing data filled in
    """
    validated_repos = []

    for repo in scored_repos:
        # Ensure basic fields exist
        name = repo.get("name") or (
            repo.get("full_name", "").split("/")[-1]
            if repo.get("full_name")
            else "Unknown"
        )
        full_name = repo.get("full_name") or f"unknown/{name}"

        if not repo.get("description"):
            repo["description"] = f"A GitHub repository: {name}"

        if not repo.get("html_url") and not repo.get("url"):
            repo["html_url"] = f"https://github.com/{full_name}"

        # Ensure we have a score
        if "score" not in repo:
            repo["score"] = 0

        # Ensure score is numeric
        try:
            repo["score"] = float(repo["score"])
        except (ValueError, TypeError):
            repo["score"] = 0

        # Ensure we have metrics
        if "score_details" not in repo or "metrics" not in repo["score_details"]:
            repo["score_details"] = repo.get("score_details", {})
            repo["score_details"]["metrics"] = {
                "stars": 0,
                "stars_gained_14d": 0,
                "forks": 0,
                "forks_gained_14d": 0,
                "commits_14d": 0,
                "contributors_30d": 0,
                "avg_issue_resolution_days": 30,
            }

        # Copy essential fields to the top level if needed
        if "score_details" in repo and "metrics" in repo["score_details"]:
            if "stars" not in repo:
                repo["stars"] = repo["score_details"]["metrics"].get("stars", 0)
            if "forks" not in repo:
                repo["forks"] = repo["score_details"]["metrics"].get("forks", 0)

        validated_repos.append(repo)

    return validated_repos


def main():
    """Main entry point for the CLI."""
    # Parse arguments
    args = parse_args()

    # Print debug info if requested
    if args.debug:
        debug_env_vars()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(level=log_level)
    logger.info("Starting Weekly Dev Tools Gems CLI")

    # Load configuration
    config = Config(args.config)

    # Set up GitHub client if token available
    github_client = None
    github_token = args.github_token or os.environ.get("GITHUB_TOKEN")

    if github_token:
        if args.debug:
            # Don't log the full token in debug mode, just the first few chars
            token_preview = (
                github_token[:4] + "..." if len(github_token) > 4 else "[empty]"
            )
            token_source = (
                "command line" if args.github_token else "environment variable"
            )
            logger.debug(
                f"Using GitHub token from {token_source} (starts with: {token_preview})"
            )

        try:
            # Validate the GitHub token
            is_valid, validation_message = validate_github_token(github_token)
            if is_valid:
                github_client = Github(github_token)
                logger.info(
                    f"GitHub API client initialized successfully: {validation_message}"
                )

                # Handle --verify-token flag
                if args.verify_token:
                    logger.info("✅ Token verification successful!")
                    return 0

            else:
                logger.error(f"GitHub token validation failed: {validation_message}")
                logger.warning("GitHub API client not initialized due to invalid token")
                github_client = None

                # Handle --verify-token flag for invalid token
                if args.verify_token:
                    logger.error("❌ Token verification failed!")
                    return 1

        except Exception as e:
            logger.error(f"Error initializing GitHub API client: {str(e)}")
            github_client = None

            # Handle --verify-token flag for error case
            if args.verify_token:
                logger.error("❌ Token verification failed with error!")
                return 1

    else:
        logger.warning("GITHUB_TOKEN not found - some scoring features will be limited")
        logger.debug("To fix this, you can:")
        logger.debug("1. Create a .env file with GITHUB_TOKEN=your_token")
        logger.debug(
            "2. Set it as an environment variable: export GITHUB_TOKEN=your_token"
        )
        logger.debug("3. Pass it as a CLI argument: --github-token=your_token")

        # Handle --verify-token flag when no token is found
        if args.verify_token:
            logger.error("❌ No GitHub token found to verify")
            return 1

    # Debug: Print environment variables
    debug_env_vars()

    # Step 1: Collect data from sources
    all_repos = []

    # Collect from GitHub Trending
    logger.info("Collecting from GitHub Trending")
    trending_collector = TrendingCollector(config)
    trending_repos = trending_collector.collect(
        timespan="weekly", max_repos=args.max_repos
    )
    logger.info(f"Collected {len(trending_repos)} trending repositories")
    all_repos.extend(trending_repos)

    # Collect from Product Hunt (if not skipped)
    if not args.skip_producthunt:
        logger.info("Collecting from Product Hunt")
        ph_collector = ProductHuntCollector(config)
        ph_products = ph_collector.collect(min_upvotes=50, max_products=args.max_repos)

        # Try to match with GitHub repositories
        ph_repos = []
        for product in ph_products:
            repo_name = ph_collector.match_with_github_repo(product)
            if repo_name:
                # Found a GitHub repo match
                # In a real implementation, we would fetch repo details
                # For MVP, we'll create a simple placeholder with the data we have
                ph_repos.append(
                    {
                        "full_name": repo_name,
                        "name": repo_name.split("/")[-1]
                        if "/" in repo_name
                        else repo_name,
                        "html_url": f"https://github.com/{repo_name}",
                        "description": product.get("tagline", ""),
                        "ph_url": product.get("ph_url", ""),
                        "ph_upvotes": product.get("upvotes", 0),
                        "source": "product_hunt",
                    }
                )

        logger.info(f"Matched {len(ph_repos)} Product Hunt products with GitHub repos")
        all_repos.extend(ph_repos)

    # Collect from Hacker News (if not skipped)
    if not args.skip_hackernews:
        logger.info("Collecting from Hacker News")
        hn_collector = ShowHNCollector(config)
        hn_stories = hn_collector.collect(
            min_points=50, max_posts=args.max_repos, days_back=7
        )

        # Try to match with GitHub repositories
        hn_repos = []
        for story in hn_stories:
            repo_name = hn_collector.match_with_github_repo(story)
            if repo_name:
                # Found a GitHub repo match
                hn_repos.append(
                    {
                        "full_name": repo_name,
                        "name": repo_name.split("/")[-1]
                        if "/" in repo_name
                        else repo_name,
                        "html_url": f"https://github.com/{repo_name}",
                        "description": story.get("title", ""),
                        "hn_url": story.get("hn_url", ""),
                        "hn_points": story.get("points", 0),
                        "source": "hacker_news",
                    }
                )

        logger.info(f"Matched {len(hn_repos)} Hacker News stories with GitHub repos")
        all_repos.extend(hn_repos)

    # Deduplicate repositories by full_name
    unique_repos = {}
    for repo in all_repos:
        full_name = repo.get("full_name")
        if full_name and full_name not in unique_repos:
            unique_repos[full_name] = repo
        elif full_name in unique_repos:
            # Merge data from multiple sources
            unique_repos[full_name].update(
                {k: v for k, v in repo.items() if k not in unique_repos[full_name]}
            )

    all_repos = list(unique_repos.values())
    logger.info(f"Total unique repositories: {len(all_repos)}")

    # Step 2: Score repositories
    logger.info("Scoring repositories")
    momentum_scorer = MomentumScorer(config, github_client, logger)

    scored_repos = []
    for repo in all_repos:
        try:
            score, details = momentum_scorer.score_repository(repo)
            repo_with_score = {**repo, "score": score, "score_details": details}
            scored_repos.append(repo_with_score)
            logger.debug(f"Scored {repo.get('full_name', 'unknown')} with {score}/10")
        except Exception as e:
            logger.error(f"Error scoring {repo.get('full_name', 'unknown')}: {str(e)}")

    # Validate data before generating report
    logger.info("Validating repository data")
    validated_repos = validate_data(scored_repos)
    logger.info(
        f"Validated repository data: {len(validated_repos)} repositories ready for output"
    )

    # Step 3: Generate report
    logger.info("Generating weekly report")
    report_generator = WeeklyGemsReportGenerator(config)
    report_path = report_generator.generate_report(validated_repos)

    # Step 4: Generate API JSON (if not skipped)
    if not args.skip_api:
        logger.info("Generating API JSON for dashboard")
        generated_files = generate_api_json(validated_repos, datetime.datetime.now())
        logger.info(f"API JSON files generated: {', '.join(generated_files.values())}")

    logger.info(f"Weekly Dev Tools Gems report generated: {report_path}")
    print(f"\nReport generated: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
