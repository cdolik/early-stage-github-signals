import pytest
from src.generators.json_generator import JSONGenerator
from datetime import datetime

def test_score_delta_and_trend():
    previous_scores = {"test/repo": 7.0}
    previous_trends = {"test/repo": [6.8, 7.0]}
    repo = {
        "name": "repo",
        "full_name": "test/repo",
        "html_url": "https://github.com/test/repo",
        "description": "Test repo",
        "score": 8.1,
        "score_details": {},
        "language": "Python",
        "stars": 100,
        "forks": 10,
        "topics": [],
        "created_at": "2025-01-01T00:00:00Z"
    }
    gen = JSONGenerator()
    formatted = gen._format_repos_for_api([repo], previous_scores, previous_trends)
    assert formatted[0]["score_change"] == 1.1
    assert formatted[0]["trend"] == [7.0, 8.1]
