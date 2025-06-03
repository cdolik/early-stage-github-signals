"""
Integration test for the Early Stage GitHub Signals Platform.

This script tests the end-to-end functionality of the platform without making actual API calls.
"""
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config import Config
from src.collectors.github_collector import GitHubCollector
from src.collectors.hackernews_collector import HackerNewsCollector
from src.analyzers.startup_scorer import StartupScorer
from src.generators.report_generator import ReportGenerator
from src.generators.html_generator import HtmlGenerator
from src.generators.api_generator import ApiGenerator


class TestIntegration(unittest.TestCase):
    """Test the end-to-end integration of the platform."""
    
    def setUp(self):
        """Set up test case."""
        # Create a mock config
        self.config = Config()
        
        # Mock cache
        self.cache = MagicMock()
        self.cache.get.return_value = None
        self.cache.set.return_value = None
        
    @patch('src.collectors.github_collector.Github')
    def test_github_collector(self, mock_github):
        """Test GitHub collector functionality."""
        # Setup mock repository data
        mock_repo = MagicMock()
        mock_repo.id = 12345
        mock_repo.full_name = "test/repo"
        mock_repo.name = "repo"
        mock_repo.owner.login = "test"
        mock_repo.owner.type = "Organization"
        mock_repo.owner.id = 67890
        mock_repo.owner.html_url = "https://github.com/test"
        mock_repo.html_url = "https://github.com/test/repo"
        mock_repo.description = "Test repository"
        mock_repo.created_at = "2023-01-01T00:00:00Z"
        mock_repo.updated_at = "2023-01-02T00:00:00Z"
        mock_repo.pushed_at = "2023-01-02T00:00:00Z"
        mock_repo.language = "Python"
        mock_repo.stargazers_count = 100
        mock_repo.watchers_count = 50
        mock_repo.forks_count = 25
        mock_repo.open_issues_count = 5
        mock_repo.topics = ["api", "startup", "saas"]
        mock_repo.has_wiki = True
        mock_repo.has_pages = True
        mock_repo.has_projects = True
        mock_repo.has_downloads = True
        mock_repo.license = None
        mock_repo.default_branch = "main"
        
        # Set up search results
        mock_search_result = MagicMock()
        mock_search_result.totalCount = 1
        mock_search_result.__iter__ = lambda self: iter([mock_repo])
        
        # Configure mock GitHub client
        mock_github_instance = mock_github.return_value
        mock_github_instance.search_repositories.return_value = mock_search_result
        mock_github_instance.get_repo.return_value = mock_repo
        
        # Test collector
        collector = GitHubCollector(self.config, self.cache)
        repositories = collector.collect(days=7, max_repos=1)
        
        # Assertions
        self.assertEqual(len(repositories), 1)
        self.assertEqual(repositories[0]['full_name'], "test/repo")
        self.assertEqual(repositories[0]['language'], "Python")
        
    def test_startup_scorer(self):
        """Test startup scoring functionality."""
        # Create mock repository data
        mock_repo = {
            'id': 12345,
            'full_name': "test/repo",
            'name': "repo",
            'owner': {
                'login': "test",
                'type': "Organization",
                'id': 67890,
                'url': "https://github.com/test"
            },
            'html_url': "https://github.com/test/repo",
            'description': "A test SaaS startup repository",
            'created_at': "2023-01-01T00:00:00Z",
            'updated_at': "2023-01-02T00:00:00Z",
            'pushed_at': "2023-01-02T00:00:00Z",
            'language': "Python",
            'stargazers_count': 100,
            'watchers_count': 50,
            'forks_count': 25,
            'open_issues_count': 5,
            'topics': ["api", "startup", "saas"],
            'has_wiki': True,
            'has_pages': True,
            'has_projects': True,
            'has_downloads': True,
            'license': None,
            'default_branch': "main",
            'ci_cd_setup': True,
            'has_tests': True,
            'readme_quality': {'score': 2.0, 'exists': True},
            'commit_activity': {'weekly_commits': 15, 'unique_authors': 3},
            'external_website': "https://example.com",
            'organization': {
                'login': "test",
                'name': "Test Org",
                'blog': "https://test.org",
                'email': "info@test.org",
                'bio': "We're a startup doing cool things",
                'location': "San Francisco, CA",
                'public_repos': 10,
                'followers': 50,
                'created_at': "2022-12-01T00:00:00Z",
                'updated_at': "2023-01-01T00:00:00Z",
                'has_website': True,
                'hiring_indicators': True,
                'team_size': 5
            },
            'contributors': {
                'total_count': 10,
                'external_count': 5
            }
        }
        
        # Mock Hacker News data
        mock_hn = {
            'title': "Test Repository Launch",
            'points': 100,
            'comment_count': 50,
            'urls': ["https://github.com/test/repo"]
        }
        
        # Test scorer
        scorer = StartupScorer(self.config, [mock_repo], [mock_hn])
        scored_repos = scorer.score_repositories()
        
        # Assertions
        self.assertEqual(len(scored_repos), 1)
        self.assertTrue('total_score' in scored_repos[0])
        self.assertTrue(scored_repos[0]['total_score'] > 0)
        
    def test_generators(self):
        """Test report generators functionality."""
        # Create mock scored repository
        mock_scored_repo = {
            'repository': "test/repo",
            'total_score': 35,
            'repository_score': {'total': 15},
            'organization_score': {'total': 10},
            'community_score': {'total': 10},
            'confidence_level': "high"
        }
        
        # Create mock report data
        mock_report_data = {
            'repositories': [mock_scored_repo],
            'trends': {'top_languages': ['Python', 'JavaScript']},
            'insights': {'summary': 'Test insights'},
            'date': '2023-01-01',
            'generated_at': '2023-01-01 12:00:00'
        }
        
        # Test API generator
        with patch('builtins.open', MagicMock()), \
             patch('os.makedirs', MagicMock()):
            api_gen = ApiGenerator()
            api_gen.generate = MagicMock(return_value='/path/to/api.json')
            api_path = api_gen.generate(mock_report_data)
            self.assertIsNotNone(api_path)
        
        # Test HTML generator
        with patch('builtins.open', MagicMock()), \
             patch('os.makedirs', MagicMock()), \
             patch('jinja2.Environment', MagicMock()):
            html_gen = HtmlGenerator()
            html_gen.generate = MagicMock(return_value='/path/to/index.html')
            html_path = html_gen.generate(mock_report_data)
            self.assertIsNotNone(html_path)


if __name__ == '__main__':
    unittest.main()
