"""
GitHub Trending collector for the Early Stage GitHub Signals platform.
Scrapes GitHub Trending page without using API calls.
"""
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import timezone
import re
from typing import Dict, List, Any, Optional

from .base_collector import BaseCollector


class TrendingCollector(BaseCollector):
    """
    Collector for GitHub Trending repositories without using API calls.
    """
    
    def __init__(self, config=None, cache=None, logger=None):
        """
        Initialize the trending collector.
        
        Args:
            config: Configuration manager (optional)
            cache: Cache manager (optional)
            logger: Logger instance (optional)
        """
        super().__init__(config, cache, logger)
        self.base_url = "https://github.com/trending"
        self.session = requests.Session()
        self.dev_tool_topics = [
            "devops", "cli", "sdk", "api", "developer-tools", "devtools", 
            "library", "framework", "tooling", "infrastructure"
        ]
        self.dev_tool_languages = ["python", "typescript", "rust", "go", "javascript"]
        
    def get_name(self) -> str:
        """Get the collector name."""
        return "GitHubTrending"
        
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect trending repositories without using API calls.
        
        Args:
            timespan: daily, weekly, or monthly (default: weekly)
            language: Filter by programming language (optional)
            
        Returns:
            List of trending repository data
        """
        self.logger.info("Collecting GitHub trending repositories...")
        
        # Extract parameters
        timespan = kwargs.get('timespan', 'weekly')
        language = kwargs.get('language')
        max_repos = kwargs.get('max_repos', 25)
        
        # Get trending repositories
        trending_repos = self._get_trending_repos(timespan, language)
        
        # Filter for developer tools
        dev_tools_repos = self._filter_dev_tools(trending_repos)
        
        # Filter by age (2-12 months old)
        age_filtered_repos = self._filter_by_age(dev_tools_repos)
        
        # Sort by score and limit results
        sorted_repos = sorted(age_filtered_repos, key=lambda x: x.get('trending_score', 0), reverse=True)
        result = sorted_repos[:max_repos]
        
        self.logger.info(f"Collected {len(result)} trending repositories")
        return result
        
    def _get_trending_repos(self, timespan: str = 'weekly', language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scrape GitHub trending page for repositories."""
        url = self.base_url
        
        # Add language filter if specified
        if language:
            url += f"/{language}"
            
        # Add timespan parameter
        if timespan in ['daily', 'weekly', 'monthly']:
            url += f"?since={timespan}"
            
        self.logger.debug(f"Scraping trending from: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all repository boxes
            repo_boxes = soup.select('article.Box-row')
            
            repos = []
            for box in repo_boxes:
                try:
                    # Extract repo full_name (owner/name)
                    name_element = box.select_one('h2.h3 a')
                    if not name_element:
                        continue
                        
                    full_name = name_element.get_text(strip=True).replace(' ', '')
                    
                    # Extract description
                    desc_element = box.select_one('p')
                    description = desc_element.get_text(strip=True) if desc_element else ""
                    
                    # Extract stars
                    stars_element = box.select_one('a.Link--muted:nth-of-type(1)')
                    stars_text = stars_element.get_text(strip=True) if stars_element else "0"
                    stars = self._parse_number(stars_text)
                    
                    # Extract forks
                    forks_element = box.select_one('a.Link--muted:nth-of-type(2)')
                    forks_text = forks_element.get_text(strip=True) if forks_element else "0"
                    forks = self._parse_number(forks_text)
                    
                    # Extract language
                    lang_element = box.select_one('span[itemprop="programmingLanguage"]')
                    language = lang_element.get_text(strip=True) if lang_element else None
                    
                    # Extract today's stars
                    today_stars_element = box.select_one('span.d-inline-block.float-sm-right')
                    today_stars_text = today_stars_element.get_text(strip=True) if today_stars_element else "0"
                    today_stars = self._parse_number(today_stars_text.replace('stars today', '').strip())
                    
                    repo_data = {
                        'full_name': full_name,
                        'name': full_name.split('/')[-1] if '/' in full_name else full_name,
                        'owner': full_name.split('/')[0] if '/' in full_name else "",
                        'html_url': f"https://github.com/{full_name}",
                        'description': description,
                        'stars': stars,
                        'forks': forks,
                        'language': language,
                        'trending_stars': today_stars,
                        'trending_timespan': timespan,
                        'trending_score': self._calculate_trending_score(stars, today_stars, timespan),
                        'source': 'github_trending'
                    }
                    
                    repos.append(repo_data)
                    
                except Exception as e:
                    self.logger.error(f"Error parsing trending repo: {str(e)}")
            
            return repos
            
        except Exception as e:
            self.logger.error(f"Error scraping GitHub trending: {str(e)}")
            return []
    
    def _filter_dev_tools(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter repositories for developer tools."""
        dev_tools = []
        
        for repo in repos:
            # Check if repo language is in dev tool languages
            if repo.get('language') and repo.get('language').lower() in self.dev_tool_languages:
                dev_tools.append(repo)
                continue
                
            # Check description for dev tool keywords
            description = repo.get('description', '').lower()
            if any(keyword in description for keyword in self.dev_tool_topics):
                dev_tools.append(repo)
                continue
                
            # We'll need to get topics separately for each repo
            # This would require API calls or additional scraping
            # For MVP, we'll rely on language and description only
        
        return dev_tools
        
    def _filter_by_age(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter repos by age (2-12 months old).
        Note: This requires an API call or additional scraping per repo.
        For MVP, we'll keep all repos and rely on manual verification.
        """
        # For a true age filter, we'd need to:
        # 1. Get creation date for each repo (API call or page scrape)
        # 2. Calculate age and filter out repos outside 2-12 month window
        
        # For MVP, we'll return all repos and note this limitation
        self.logger.info("Age filtering requires API calls - skipping for MVP. Will require manual verification.")
        return repos
        
    def _parse_number(self, text: str) -> int:
        """Parse number from text like '1.2k' or '123'"""
        if not text:
            return 0
            
        text = text.replace(',', '').strip()
        
        # Handle 'k', 'm', etc.
        multipliers = {
            'k': 1000,
            'm': 1000000
        }
        
        for suffix, multiplier in multipliers.items():
            if suffix in text.lower():
                try:
                    number = float(text.lower().replace(suffix, '').strip())
                    return int(number * multiplier)
                except ValueError:
                    return 0
        
        # Regular number
        try:
            return int(float(text))
        except ValueError:
            return 0
            
    def _calculate_trending_score(self, total_stars: int, period_stars: int, timespan: str) -> float:
        """Calculate trending score based on stars."""
        # Simple score based on period stars with a bonus for trending repositories
        # with fewer total stars (to surface newer repositories)
        
        # Base score is the period stars
        score = period_stars
        
        # Bonus for repositories with fewer total stars (newer repositories)
        if total_stars < 100:
            score *= 1.5
        elif total_stars < 500:
            score *= 1.2
            
        # Adjust for timespan
        if timespan == 'daily':
            score *= 1.0  # Daily trending is very volatile
        elif timespan == 'weekly':
            score *= 1.2  # Weekly trending is more stable
        elif timespan == 'monthly':
            score *= 0.8  # Monthly might include more established projects
            
        return score
