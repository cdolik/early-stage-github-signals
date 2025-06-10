"""
Hacker News Show HN collector for the Early Stage GitHub Signals platform.
Collects Show HN posts with 50+ points without excessive API usage.
"""
import requests
import time
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

from .base_collector import BaseCollector


class ShowHNCollector(BaseCollector):
    """
    Collector for Hacker News Show HN posts.
    Uses the official Hacker News API which doesn't have rate limits.
    """
    
    def __init__(self, config=None, cache=None, logger=None):
        """
        Initialize the Show HN collector.
        
        Args:
            config: Configuration manager (optional)
            cache: Cache manager (optional)
            logger: Logger instance (optional)
        """
        super().__init__(config, cache, logger)
        self.base_url = "https://hacker-news.firebaseio.com/v0"
        self.session = requests.Session()
        
    def get_name(self) -> str:
        """Get the collector name."""
        return "ShowHN"
        
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect Show HN posts with high points.
        
        Args:
            min_points: Minimum number of points (default: 50)
            max_posts: Maximum number of posts to return (default: 25)
            days_back: How many days back to check (default: 7)
            
        Returns:
            List of Show HN post data
        """
        self.logger.info("Collecting Show HN posts...")
        
        # Extract parameters
        min_points = kwargs.get('min_points', 50)
        max_posts = kwargs.get('max_posts', 25)
        days_back = kwargs.get('days_back', 7)
        
        # Get recent Show HN stories
        stories = self._get_show_hn_stories(days_back)
        
        # Filter by points
        filtered_stories = [s for s in stories if s.get('points', 0) >= min_points]
        
        # Filter for developer tools
        dev_tools_stories = self._filter_dev_tools(filtered_stories)
        
        # Sort by points and limit results
        sorted_stories = sorted(dev_tools_stories, key=lambda x: x.get('points', 0), reverse=True)
        result = sorted_stories[:max_posts]
        
        self.logger.info(f"Collected {len(result)} Show HN posts")
        return result
        
    def _get_show_hn_stories(self, days_back: int) -> List[Dict[str, Any]]:
        """Get Show HN stories from the last X days."""
        try:
            # Get recent Show HN story IDs
            show_hn_url = f"{self.base_url}/showstories.json"
            response = self.session.get(show_hn_url, timeout=10)
            response.raise_for_status()
            story_ids = response.json()
            
            # Time threshold
            threshold = datetime.now(timezone.utc) - timedelta(days=days_back)
            threshold_timestamp = int(threshold.timestamp())
            
            # Get story details (limit API calls)
            stories = []
            for story_id in story_ids[:100]:  # Only check the most recent 100 stories
                try:
                    # Get story details
                    story_url = f"{self.base_url}/item/{story_id}.json"
                    response = self.session.get(story_url, timeout=10)
                    response.raise_for_status()
                    story = response.json()
                    
                    # Check if it's a Show HN post and recent enough
                    if (story.get('type') == 'story' and
                        'show hn' in story.get('title', '').lower() and
                        story.get('time', 0) >= threshold_timestamp):
                        
                        # Extract data
                        stories.append({
                            'id': story.get('id'),
                            'title': story.get('title', '').replace('Show HN: ', ''),
                            'url': story.get('url', ''),
                            'hn_url': f"https://news.ycombinator.com/item?id={story.get('id')}",
                            'points': story.get('score', 0),
                            'comments': story.get('descendants', 0),
                            'created_at': datetime.fromtimestamp(story.get('time', 0), tz=timezone.utc).isoformat(),
                            'author': story.get('by', ''),
                            'source': 'hacker_news'
                        })
                    
                    # Don't hit the API too hard
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"Error fetching story {story_id}: {str(e)}")
                    continue
            
            return stories
            
        except Exception as e:
            self.logger.error(f"Error fetching Show HN stories: {str(e)}")
            return []
    
    def _filter_dev_tools(self, stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter stories for developer tools."""
        # Dev tools keywords
        dev_keywords = [
            'developer', 'dev tool', 'sdk', 'api', 'library', 'framework',
            'cli', 'command line', 'devops', 'tooling', 'infrastructure',
            'code', 'coding', 'programmer', 'github', 'git', 'repository',
            'deployment', 'continuous', 'integration', 'testing', 'debugging'
        ]
        
        dev_tools = []
        
        for story in stories:
            title = story.get('title', '').lower()
            
            # Check if story title contains dev tool keywords
            if any(keyword.lower() in title for keyword in dev_keywords):
                dev_tools.append(story)
                
        return dev_tools
        
    def match_with_github_repo(self, story: Dict[str, Any]) -> Optional[str]:
        """
        Try to find a GitHub repo URL from the story data.
        Returns the GitHub repo full name or None if not found.
        """
        url = story.get('url', '')
        
        # Direct GitHub URLs
        if 'github.com' in url:
            match = re.search(r'github\.com/([^/]+/[^/]+)', url)
            if match:
                return match.group(1)
        
        # For non-GitHub URLs, we would need to:
        # 1. Visit the story URL
        # 2. Look for GitHub links in the page
        # 3. Extract repo name from those links
        
        # This is more intensive and would be a good enhancement for later
        return None
