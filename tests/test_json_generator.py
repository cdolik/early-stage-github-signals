"""
Unit tests for the JSON generator.
"""
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
import pytest

from src.generators.json_generator import JSONGenerator
from tests.fixtures.sample_repos import SAMPLE_REPOS


class TestJSONGenerator:
    """Tests for the JSON generator."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temp directories for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.api_dir = self.temp_path / 'docs' / 'api'
        self.data_dir = self.temp_path / 'docs' / 'data'
        
        # Initialize generator with temp paths
        self.generator = JSONGenerator()
        self.generator.api_dir = self.api_dir
        self.generator.data_dir = self.data_dir
        
        # Ensure directories exist
        self.api_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_generate_creates_files(self):
        """Test that generate creates the expected files."""
        # Set a fixed date for testing
        test_date = datetime(2025, 6, 6)
        
        # Generate JSON files
        result = self.generator.generate(SAMPLE_REPOS, test_date)
        
        # Check that files were created
        assert (self.api_dir / 'latest.json').exists()
        assert (self.data_dir / '2025-06-06.json').exists()
        
        # Check paths in result
        assert result['latest'] == str(self.api_dir / 'latest.json')
        assert result['dated'] == str(self.data_dir / '2025-06-06.json')
    
    def test_json_schema_structure(self):
        """Test that the JSON has the expected schema."""
        # Generate JSON files
        self.generator.generate(SAMPLE_REPOS)
        
        # Load and check latest.json
        with open(self.api_dir / 'latest.json', 'r') as f:
            data = json.load(f)
        
        # Check that it's an API object with repositories
        assert isinstance(data, dict)
        assert 'repositories' in data
        assert 'date' in data
        assert 'name' in data
        assert 'date_generated' in data
        
        repositories = data['repositories']
        assert isinstance(repositories, list)
        assert len(repositories) == len(SAMPLE_REPOS)
        
        # Check first repo structure
        repo = repositories[0]
        assert 'name' in repo
        assert 'repo_url' in repo
        assert 'score' in repo
        assert 'signals' in repo
        assert 'ecosystem' in repo
        assert 'why_matters' in repo
        
        # Check signals structure
        signals = repo['signals']
        assert isinstance(signals, dict)
    
    def test_sorting_by_score(self):
        """Test that repositories are sorted by score."""
        # Generate JSON files
        self.generator.generate(SAMPLE_REPOS)
        
        # Load latest.json
        with open(self.api_dir / 'latest.json', 'r') as f:
            data = json.load(f)
        
        # Check sorting
        repositories = data['repositories']
        scores = [repo['score'] for repo in repositories]
        assert scores == sorted(scores, reverse=True)
    
    def test_why_matters_generation(self):
        """Test generation of why_matters field."""
        # Generate JSON files
        self.generator.generate(SAMPLE_REPOS)
        
        # Load latest.json
        with open(self.api_dir / 'latest.json', 'r') as f:
            data = json.load(f)
        
        # Check why_matters for first repo
        repositories = data['repositories']
        assert repositories[0]['why_matters']
        assert len(repositories[0]['why_matters']) <= 80  # Should be limited to 80 chars
        
        # It should contain bullet points
        assert '•' in repositories[0]['why_matters']
