"""
Initialization file for collectors module.
"""

from .base_collector import BaseCollector
from .github_collector import GitHubCollector
from .hackernews_collector import HackerNewsCollector

__all__ = [
    'BaseCollector',
    'GitHubCollector',
    'HackerNewsCollector',
]
