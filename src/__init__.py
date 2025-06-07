"""
Early Stage GitHub Signals Platform

This package contains modules for collecting, analyzing, and reporting on GitHub repositories
with high startup potential.
"""

__version__ = "1.0.0"

# Export key constants
QUALITY_THRESHOLD = 7.0  # Minimum score (out of 10) to be featured
DEFAULT_MAX_REPOS = 100  # Default limit for repositories to analyze
DEFAULT_CACHE_TTL = 86400  # Default cache TTL (24 hours)

# Scoring weights
WEIGHTS = {
    "commit_surge": 3.0,
    "star_velocity": 3.0,
    "team_traction": 2.0,
    "ecosystem_fit": 2.0
}

# Package exports
from .analyzers import momentum_scorer, insights_generator
from .collectors import github_collector, trending_collector
from .generators import report_generator, api_generator
from .utils import config, logger
