"""
Hacker News data collector for the Early Stage GitHub Signals platform.
"""
import datetime
import time
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import requests

from .base_collector import BaseCollector
from ..utils import format_date, parse_date, rate_limited_request


class HackerNewsCollector(BaseCollector):
    """
    Collector for Hacker News data related to GitHub repositories.
    """
    
    def __init__(self, config=None, cache=None):
        """
        Initialize the Hacker News collector.
        
        Args:
            config: Configuration manager (optional)
            cache: Cache manager (optional)
        """
        super().__init__(config, cache)
        self.base_url = self.config.get('hackernews.base_url',
                                      "https://hacker-news.firebaseio.com/v0")
        self.session = requests.Session()
        
    def get_name(self) -> str:
        """
        Get the name of the collector.
        
        Returns:
            The collector name
        """
        return "HackerNews"
        
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect Hacker News stories mentioning GitHub repositories.
        
        Args:
            **kwargs: Collection parameters:
                - days: Number of days to look back (default from config)
                - points_threshold: Minimum points for stories (default from config)
                - repos: List of repository full names to check (optional)
                
        Returns:
            List of Hacker News stories data
        """
        days = kwargs.get('days', self.config.get('hackernews.lookback_days', 30))
        points_threshold = kwargs.get('points_threshold',
                                   self.config.get('hackernews.points_threshold', 5))
        repos = kwargs.get('repos', [])
        
        # Calculate the date threshold
        date_threshold = datetime.datetime.now() - datetime.timedelta(days=days)
        
        self.logger.info(f"Collecting Hacker News stories from the last {days} days")
        
        # Get recent stories from HN
        stories = self._get_recent_stories(date_threshold, points_threshold)
        
        # If specific repositories are provided, filter for those
        if repos:
            repo_set = set(repos)
            filtered_stories = []
            
            for story in stories:
                if any(repo in story.get('url', '') for repo in repo_set):
                    filtered_stories.append(story)
                    continue
                    
                # Check if the repository is mentioned in the title
                for repo in repo_set:
                    # Extract owner/name from repo full name
                    if '/' in repo:
                        owner, name = repo.split('/', 1)
                        if name.lower() in story.get('title', '').lower():
                            filtered_stories.append(story)
                            break
                            
            stories = filtered_stories
            
        # Otherwise, filter for GitHub URLs
        else:
            stories = [s for s in stories if self._is_github_repo_url(s.get('url', ''))]
            
        self.logger.info(f"Found {len(stories)} relevant Hacker News stories")
        
        # Enrich stories with comments data
        return self._enrich_stories(stories)
        
    def _get_recent_stories(
        self,
        date_threshold: datetime.datetime,
        points_threshold: int
    ) -> List[Dict[str, Any]]:
        """
        Get recent stories from Hacker News.
        
        Args:
            date_threshold: Minimum date for stories
            points_threshold: Minimum points for stories
            
        Returns:
            List of Hacker News stories
        """
        stories = []
        
        # Get top stories first
        top_story_ids = self._get_story_ids("topstories.json")
        if not top_story_ids:
            return []
            
        # Then get new stories
        new_story_ids = self._get_story_ids("newstories.json")
        if new_story_ids:
            # Merge and deduplicate story IDs
            all_story_ids = list(set(top_story_ids + new_story_ids))
        else:
            all_story_ids = top_story_ids
            
        self.logger.info(f"Found {len(all_story_ids)} stories to process")
        
        # Process stories in batches to avoid overloading the API
        batch_size = 50
        for i in range(0, len(all_story_ids), batch_size):
            batch_ids = all_story_ids[i:i + batch_size]
            
            # Get details for each story in the batch
            for story_id in batch_ids:
                try:
                    story = self._get_item(story_id)
                    
                    # Filter by date and points
                    if story and 'time' in story:
                        story_date = datetime.datetime.fromtimestamp(story['time'])
                        
                        if (story_date >= date_threshold and
                            story.get('score', 0) >= points_threshold and
                            story.get('type') == 'story' and
                            'url' in story):
                            stories.append(story)
                except Exception as e:
                    self.logger.warning(f"Error getting story {story_id}: {e}")
                    continue
                    
            # Avoid rate limiting
            time.sleep(0.5)
            
        return stories
        
    def _is_github_repo_url(self, url: str) -> bool:
        """
        Check if a URL is a GitHub repository URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is a GitHub repository, False otherwise
        """
        if not url:
            return False
            
        # Common GitHub repository URL patterns
        patterns = [
            r'https?://github\.com/[^/]+/[^/]+/?$',
            r'https?://github\.com/[^/]+/[^/]+/(?:releases|tags)'
        ]
        
        # Check against patterns
        for pattern in patterns:
            if re.match(pattern, url):
                return True
                
        return False
        
    def _extract_github_repo_from_url(self, url: str) -> Optional[str]:
        """
        Extract GitHub repository full name from a URL.
        
        Args:
            url: GitHub URL
            
        Returns:
            Repository full name (owner/name) or None if not a repo URL
        """
        if not url:
            return None
            
        github_repo_pattern = r'https?://github\.com/([^/]+/[^/]+)/?(?:\?.*)?$'
        match = re.match(github_repo_pattern, url)
        
        if match:
            return match.group(1)
            
        # Handle other GitHub URL formats
        github_other_pattern = r'https?://github\.com/([^/]+/[^/]+)/.+'
        match = re.match(github_other_pattern, url)
        
        if match:
            return match.group(1)
            
        return None
        
    def _enrich_stories(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich Hacker News stories with additional data.
        
        Args:
            stories: List of basic Hacker News stories
            
        Returns:
            List of enriched story data
        """
        enriched_stories = []
        
        for story in stories:
            try:
                enriched_story = story.copy()
                
                # Extract GitHub repository info
                repo_full_name = self._extract_github_repo_from_url(story.get('url', ''))
                enriched_story['github_repo'] = repo_full_name
                
                # Get comments data
                if 'kids' in story and story['kids']:
                    comments = []
                    comment_count = 0
                    
                    # Only process up to 30 comments to avoid API overload
                    for kid_id in story['kids'][:30]:
                        try:
                            comment = self._get_item(kid_id)
                            if comment and comment.get('type') == 'comment':
                                comments.append({
                                    'id': comment.get('id'),
                                    'text': comment.get('text', ''),
                                    'by': comment.get('by', ''),
                                    'time': comment.get('time', 0)
                                })
                                comment_count += 1
                                
                                # Get child comments (one level deep)
                                if 'kids' in comment:
                                    for child_id in comment['kids'][:5]:  # Limit child comments
                                        try:
                                            child_comment = self._get_item(child_id)
                                            if child_comment and child_comment.get('type') == 'comment':
                                                comments.append({
                                                    'id': child_comment.get('id'),
                                                    'text': child_comment.get('text', ''),
                                                    'by': child_comment.get('by', ''),
                                                    'time': child_comment.get('time', 0),
                                                    'parent_id': comment.get('id')
                                                })
                                                comment_count += 1
                                        except Exception:
                                            continue
                        except Exception as e:
                            self.logger.debug(f"Error getting comment {kid_id}: {e}")
                            continue
                            
                        # Avoid rate limiting
                        time.sleep(0.1)
                        
                    enriched_story['comment_count'] = len(story['kids'])
                    enriched_story['processed_comment_count'] = comment_count
                    enriched_story['comments'] = comments
                else:
                    enriched_story['comment_count'] = 0
                    enriched_story['processed_comment_count'] = 0
                    enriched_story['comments'] = []
                    
                # Calculate a score based on points and comments
                base_score = story.get('score', 0)
                comment_factor = min(story.get('descendants', 0) / 10, 5)  # Cap at 5 points
                enriched_story['hn_score'] = base_score + comment_factor
                
                enriched_stories.append(enriched_story)
                
            except Exception as e:
                self.logger.warning(f"Error enriching story {story.get('id')}: {e}")
                # Add the basic story data
                enriched_stories.append(story)
                
        return enriched_stories
        
    def _get_story_ids(self, endpoint: str) -> List[int]:
        """
        Get story IDs from a Hacker News API endpoint.
        
        Args:
            endpoint: API endpoint (e.g., 'topstories.json')
            
        Returns:
            List of story IDs
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = rate_limited_request(self.session.get, url=url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Failed to get story IDs from {endpoint}: "
                                  f"Status {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting story IDs from {endpoint}: {e}")
            return []
            
    def _get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an item (story or comment) from Hacker News by ID.
        
        Args:
            item_id: Hacker News item ID
            
        Returns:
            Item data or None if not found
        """
        url = f"{self.base_url}/item/{item_id}.json"
        
        try:
            response = rate_limited_request(self.session.get, url=url)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.debug(f"Failed to get item {item_id}: Status {response.status_code}")
                return None
        except Exception as e:
            self.logger.debug(f"Error getting item {item_id}: {e}")
            return None
