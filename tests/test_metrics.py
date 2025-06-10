import os
import json
import tempfile
from datetime import datetime, timedelta
import pytest
from src.utils.generate_metrics import calculate_metrics

@pytest.fixture
def sample_data():
    """Create sample repository data for testing."""
    now = datetime.now()
    last_week = now - timedelta(days=7)
    last_month = now - timedelta(days=35)
    
    return [
        {
            'date': now,
            'repositories': [
                {'name': 'repo1', 'score': 8},
                {'name': 'repo2', 'score': 6},
                {'name': 'repo3', 'score': 9}
            ]
        },
        {
            'date': last_week,
            'repositories': [
                {'name': 'repo4', 'score': 7},
                {'name': 'repo5', 'score': 5}
            ]
        },
        {
            'date': last_month,
            'repositories': [
                {'name': 'repo6', 'score': 8},
                {'name': 'repo7', 'score': 7}
            ]
        }
    ]

def test_calculate_metrics(sample_data):
    """Test that metrics are calculated correctly."""
    metrics = calculate_metrics(sample_data)
    
    # Check that metrics dict has the expected structure
    assert 'last_30d' in metrics
    assert 'all_time' in metrics
    
    # In our sample data, we have 3 qualifying repos (≥7) in the last 30 days
    # across 2 weeks (2 + 1), so average should be 1.5
    assert metrics['last_30d']['avg_qualifying'] == 1.5
    
    # All-time should have 4 qualifying repos across 3 weeks
    assert metrics['all_time']['avg_qualifying'] > 0
    
    # Check score calculations
    # Recent scores are [8, 6, 9, 7, 5]
    assert 7 <= metrics['last_30d']['median_score'] <= 8
    assert metrics['last_30d']['highest_score'] == 9
    
    # All scores are [8, 6, 9, 7, 5, 8, 7]
    assert 7 <= metrics['all_time']['median_score'] <= 8
    assert metrics['all_time']['highest_score'] == 9
