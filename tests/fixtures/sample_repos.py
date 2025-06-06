"""
Test fixtures for sample repositories with scoring data.
"""
import datetime

# Sample repository data for testing
SAMPLE_REPOS = [
    {
        "id": 1,
        "name": "devtoolkit",
        "full_name": "acme/devtoolkit",
        "url": "https://github.com/acme/devtoolkit",
        "html_url": "https://github.com/acme/devtoolkit",
        "description": "A complete toolkit for developers with productivity enhancers",
        "language": "TypeScript",
        "stars": 850,
        "forks": 120,
        "open_issues": 5,
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=30)).isoformat(),
        "score": 9,
        "score_details": {
            "commit_surge": 3,
            "star_velocity": 3,
            "team_traction": 2,
            "dev_ecosystem_fit": 1,
            "signals": [
                "128 commits in last 14 days (42 feature commits)",
                "350+ stars gained in last 14 days",
                "5 active contributors out of 8 total",
                "typescript language"
            ]
        },
        "topics": ["developer-tools", "productivity", "cli"]
    },
    {
        "id": 2,
        "name": "fastapi-starter",
        "full_name": "techcorp/fastapi-starter",
        "url": "https://github.com/techcorp/fastapi-starter",
        "html_url": "https://github.com/techcorp/fastapi-starter",
        "description": "Production-ready FastAPI starter template with authentication and testing",
        "language": "Python",
        "stars": 620,
        "forks": 85,
        "open_issues": 3,
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=45)).isoformat(),
        "score": 8,
        "score_details": {
            "commit_surge": 2,
            "star_velocity": 3,
            "team_traction": 2,
            "dev_ecosystem_fit": 1,
            "signals": [
                "74 commits in last 14 days (22 feature commits)",
                "250+ stars gained in last 14 days",
                "4 active contributors out of 6 total",
                "python language"
            ]
        },
        "topics": ["fastapi", "api", "python", "backend"]
    },
    {
        "id": 3,
        "name": "rust-analyzer-pro",
        "full_name": "rustify/rust-analyzer-pro",
        "url": "https://github.com/rustify/rust-analyzer-pro",
        "html_url": "https://github.com/rustify/rust-analyzer-pro",
        "description": "Enhanced Rust language server with advanced auto-completion and refactoring",
        "language": "Rust",
        "stars": 975,
        "forks": 58,
        "open_issues": 12,
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=60)).isoformat(),
        "score": 7,
        "score_details": {
            "commit_surge": 2,
            "star_velocity": 2,
            "team_traction": 2,
            "dev_ecosystem_fit": 1,
            "signals": [
                "65 commits in last 14 days (18 feature commits)",
                "130+ stars gained in last 14 days",
                "3 active contributors out of 5 total",
                "rust language"
            ]
        },
        "topics": ["rust", "lsp", "ide", "developer-tools"]
    },
    {
        "id": 4,
        "name": "devops-assistant",
        "full_name": "cloudco/devops-assistant",
        "url": "https://github.com/cloudco/devops-assistant",
        "html_url": "https://github.com/cloudco/devops-assistant",
        "description": "AI-powered assistant for DevOps automation and infrastructure management",
        "language": "Go",
        "stars": 450,
        "forks": 35,
        "open_issues": 8,
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=25)).isoformat(),
        "score": 6,
        "score_details": {
            "commit_surge": 2,
            "star_velocity": 1,
            "team_traction": 1,
            "dev_ecosystem_fit": 2,
            "signals": [
                "52 commits in last 14 days (15 feature commits)",
                "75+ stars gained in last 14 days",
                "2 active contributors out of 3 total",
                "go language",
                "developer-tools topics"
            ]
        },
        "topics": ["devops", "automation", "infrastructure", "ai"]
    },
    {
        "id": 5,
        "name": "js-test-runner",
        "full_name": "webdev/js-test-runner",
        "url": "https://github.com/webdev/js-test-runner",
        "html_url": "https://github.com/webdev/js-test-runner",
        "description": "Blazing fast JavaScript test runner with parallel execution and visual reporting",
        "language": "JavaScript",
        "stars": 320,
        "forks": 28,
        "open_issues": 4,
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=35)).isoformat(),
        "score": 5,
        "score_details": {
            "commit_surge": 1,
            "star_velocity": 1,
            "team_traction": 1,
            "dev_ecosystem_fit": 2,
            "signals": [
                "38 commits in last 14 days (10 feature commits)",
                "55+ stars gained in last 14 days",
                "2 active contributors out of 4 total",
                "javascript language",
                "developer-tools topics"
            ]
        },
        "topics": ["testing", "javascript", "developer-tools"]
    }
]
