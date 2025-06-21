#!/usr/bin/env python3
"""
Test script to verify GitHub token functionality
"""
import os
import sys
from pathlib import Path
from github import Github

# Try to load environment variables from .env
try:
    from dotenv import load_dotenv
    # Try multiple locations for .env file
    env_path = Path('/Users/coreydolik/early-stage-github-signals-1/.env')
    dotenv_loaded = load_dotenv(dotenv_path=env_path)
    if dotenv_loaded:
        print(f"Loaded environment variables from {env_path}")
    else:
        # Try relative path as fallback
        dotenv_loaded = load_dotenv()
        if dotenv_loaded:
            print("Loaded environment variables from current directory")
        else:
            print("Warning: No .env file found.")
except ImportError:
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

def main():
    # Check if GitHub token is set
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("ERROR: GITHUB_TOKEN environment variable not set")
        print("Please set it with: export GITHUB_TOKEN='your_token'")
        sys.exit(1)
    
    # Show token preview for verification
    token_preview = github_token[:4] + '...' if len(github_token) > 4 else '[empty]'
    print(f"INFO: Using GitHub token starting with: {token_preview}")
    
    # Try to authenticate and get user info
    try:
        github = Github(github_token)
        user = github.get_user()
        print(f"SUCCESS: Authenticated as {user.login}")
        
        # Test rate limit info
        rate_limit = github.get_rate_limit()
        print(f"Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit} remaining")
        
        # Test getting repo info
        print("\nTesting repository access...")
        repo = github.get_repo("menloresearch/jan")  # Using one of the repos from your report
        print(f"Repo: {repo.full_name}")
        print(f"Stars: {repo.stargazers_count}")
        print(f"Forks: {repo.forks_count}")
        
        # Get recent commits
        try:
            commits = list(repo.get_commits()[:5])  # Get up to 5 most recent commits
            print(f"\nRecent commits ({len(commits)}):")
            for commit in commits:
                commit_date = commit.commit.author.date.strftime("%Y-%m-%d")
                author = commit.commit.author.name
                message = commit.commit.message.split('\n')[0][:60]  # First line, limited to 60 chars
                print(f"- {commit_date} | {author}: {message}")
        except Exception as e:
            print(f"Error fetching commits: {str(e)}")
            
        print("\nToken is valid and working properly!")
            
    except Exception as e:
        print(f"ERROR: Failed to authenticate with GitHub: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
