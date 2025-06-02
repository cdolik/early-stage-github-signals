"""
Trend analysis module for GitHub repository data.
"""
import datetime
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from ..utils import Config, setup_logger


class TrendAnalyzer:
    """
    Analyzes trends across GitHub repositories.
    """
    
    def __init__(self):
        """
        Initialize the trend analyzer with configuration.
        """
        self.config = Config()
        self.logger = setup_logger(self.__class__.__name__)
        
    def analyze_trends(self, scored_repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze trends across scored repositories.
        
        Args:
            scored_repos: List of repositories with scores
            
        Returns:
            Dictionary of trend analysis results
        """
        self.logger.info(f"Analyzing trends across {len(scored_repos)} repositories")
        
        # Sort repositories by score
        sorted_repos = sorted(
            scored_repos, 
            key=lambda r: r.get('total_score', 0),
            reverse=True
        )
        
        # Calculate various trend metrics
        trends = {
            'language_distribution': self._analyze_language_distribution(sorted_repos),
            'topic_distribution': self._analyze_topic_distribution(sorted_repos),
            'score_distribution': self._analyze_score_distribution(sorted_repos),
            'age_distribution': self._analyze_age_distribution(sorted_repos),
            'top_stars_by_age': self._analyze_stars_by_age(sorted_repos),
            'confidence_levels': self._analyze_confidence_levels(sorted_repos),
            'organization_types': self._analyze_organization_types(sorted_repos),
        }
        
        # Add metadata
        trends['metadata'] = {
            'analyzed_at': datetime.datetime.now().isoformat(),
            'repository_count': len(scored_repos),
            'top_score': sorted_repos[0].get('total_score', 0) if sorted_repos else 0,
            'average_score': np.mean([r.get('total_score', 0) for r in scored_repos]) 
                if scored_repos else 0,
            'median_score': np.median([r.get('total_score', 0) for r in scored_repos])
                if scored_repos else 0
        }
        
        return trends
        
    def _analyze_language_distribution(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze programming language distribution across repositories.
        
        Args:
            repos: List of repositories
            
        Returns:
            Dictionary with language distribution stats
        """
        languages = [r.get('language') for r in repos if r.get('language')]
        language_counter = Counter(languages)
        
        # Get top languages
        top_languages = language_counter.most_common(10)
        
        # Calculate average scores by language
        language_scores = defaultdict(list)
        for repo in repos:
            if repo.get('language'):
                language_scores[repo['language']].append(repo.get('total_score', 0))
                
        avg_scores = {
            lang: round(np.mean(scores), 2)
            for lang, scores in language_scores.items()
            if scores
        }
        
        # Calculate language trends
        return {
            'top_languages': top_languages,
            'avg_score_by_language': avg_scores,
            'total_languages': len(language_counter)
        }
        
    def _analyze_topic_distribution(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze repository topic distribution.
        
        Args:
            repos: List of repositories
            
        Returns:
            Dictionary with topic distribution stats
        """
        # Collect all topics
        topics_counter = Counter()
        for repo in repos:
            topics = repo.get('topics', [])
            topics_counter.update(topics)
            
        # Get top topics
        top_topics = topics_counter.most_common(20)
        
        # Calculate topic trends
        return {
            'top_topics': top_topics,
            'total_topics': len(topics_counter)
        }
        
    def _analyze_score_distribution(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze score distribution across repositories.
        
        Args:
            repos: List of repositories
            
        Returns:
            Dictionary with score distribution stats
        """
        scores = [repo.get('total_score', 0) for repo in repos]
        
        if not scores:
            return {
                'min': 0,
                'max': 0,
                'mean': 0,
                'median': 0,
                'stddev': 0,
                'percentiles': {
                    '25': 0,
                    '50': 0,
                    '75': 0,
                    '90': 0,
                    '95': 0
                }
            }
            
        return {
            'min': min(scores),
            'max': max(scores),
            'mean': np.mean(scores),
            'median': np.median(scores),
            'stddev': np.std(scores),
            'percentiles': {
                '25': np.percentile(scores, 25),
                '50': np.percentile(scores, 50),
                '75': np.percentile(scores, 75),
                '90': np.percentile(scores, 90),
                '95': np.percentile(scores, 95)
            }
        }
        
    def _analyze_age_distribution(self, repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze repository age distribution.
        
        Args:
            repos: List of repositories
            
        Returns:
            Dictionary with age distribution stats
        """
        # Calculate repository ages in days
        ages = []
        age_brackets = {
            '0-30 days': 0,
            '31-60 days': 0,
            '61-90 days': 0,
            '91-180 days': 0,
            '181-365 days': 0,
            '1+ year': 0
        }
        
        for repo in repos:
            created_at = repo.get('created_at')
            if created_at:
                try:
                    created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = (datetime.datetime.now().replace(tzinfo=None) - 
                               created_date.replace(tzinfo=None)).days
                               
                    ages.append(age_days)
                    
                    # Update age brackets
                    if age_days <= 30:
                        age_brackets['0-30 days'] += 1
                    elif age_days <= 60:
                        age_brackets['31-60 days'] += 1
                    elif age_days <= 90:
                        age_brackets['61-90 days'] += 1
                    elif age_days <= 180:
                        age_brackets['91-180 days'] += 1
                    elif age_days <= 365:
                        age_brackets['181-365 days'] += 1
                    else:
                        age_brackets['1+ year'] += 1
                except (ValueError, TypeError):
                    continue
                    
        if not ages:
            return {
                'age_brackets': age_brackets,
                'min_age': 0,
                'max_age': 0,
                'mean_age': 0,
                'median_age': 0
            }
            
        return {
            'age_brackets': age_brackets,
            'min_age': min(ages),
            'max_age': max(ages),
            'mean_age': np.mean(ages),
            'median_age': np.median(ages)
        }
        
    def _analyze_stars_by_age(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze stars by repository age to find fast-growing repositories.
        
        Args:
            repos: List of repositories
            
        Returns:
            List of repositories with high star velocity
        """
        # Calculate star velocity for each repository
        star_velocities = []
        
        for repo in repos:
            created_at = repo.get('created_at')
            stars = repo.get('stargazers_count', 0)
            
            if created_at and stars:
                try:
                    created_date = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    age_days = max(1, (datetime.datetime.now().replace(tzinfo=None) - 
                                     created_date.replace(tzinfo=None)).days)
                                     
                    # Calculate stars per day
                    stars_per_day = stars / age_days
                    
                    star_velocities.append({
                        'repository': repo.get('full_name'),
                        'stars': stars,
                        'age_days': age_days,
                        'stars_per_day': stars_per_day,
                        'total_score': repo.get('total_score', 0)
                    })
                except (ValueError, TypeError):
                    continue
                    
        # Sort by stars per day
        star_velocities.sort(key=lambda x: x['stars_per_day'], reverse=True)
        
        # Return top 10
        return star_velocities[:10]
        
    def _analyze_confidence_levels(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze confidence level distribution.
        
        Args:
            repos: List of repositories
            
        Returns:
            Dictionary with confidence level counts
        """
        confidence_levels = {'high': 0, 'medium': 0, 'low': 0}
        
        for repo in repos:
            confidence = repo.get('confidence_level', 'low')
            if confidence in confidence_levels:
                confidence_levels[confidence] += 1
                
        return confidence_levels
        
    def _analyze_organization_types(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Analyze organization vs user repositories.
        
        Args:
            repos: List of repositories
            
        Returns:
            Dictionary with organization type counts
        """
        org_types = {'Organization': 0, 'User': 0, 'Unknown': 0}
        
        for repo in repos:
            owner_type = repo.get('owner', {}).get('type', 'Unknown')
            if owner_type in org_types:
                org_types[owner_type] += 1
            else:
                org_types['Unknown'] += 1
                
        return org_types
