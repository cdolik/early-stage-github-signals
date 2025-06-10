"""
Product Hunt weekly collector for the Early Stage GitHub Signals platform.
Scrapes Product Hunt for top products without using API calls.
"""
import requests
from bs4 import BeautifulSoup
import datetime
from datetime import timezone
import re
import json
from typing import Dict, List, Any, Optional

from .base_collector import BaseCollector


class ProductHuntCollector(BaseCollector):
    """
    Collector for Product Hunt trending products without using API calls.
    """
    
    def __init__(self, config=None, cache=None, logger=None):
        """
        Initialize the Product Hunt collector.
        
        Args:
            config: Configuration manager (optional)
            cache: Cache manager (optional)
            logger: Logger instance (optional)
        """
        super().__init__(config, cache, logger)
        self.base_url = "https://www.producthunt.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_name(self) -> str:
        """Get the collector name."""
        return "ProductHunt"
        
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect top weekly products from Product Hunt.
        
        Args:
            min_upvotes: Minimum number of upvotes (default: 50)
            max_products: Maximum number of products to return (default: 25)
            
        Returns:
            List of top product data
        """
        self.logger.info("Collecting Product Hunt weekly trending products...")
        
        # Extract parameters
        min_upvotes = kwargs.get('min_upvotes', 50)
        max_products = kwargs.get('max_products', 25)
        
        # Get top weekly products
        products = self._get_weekly_products()
        
        # Filter for developer tools
        dev_tools_products = self._filter_dev_tools(products)
        
        # Filter by upvotes
        upvote_filtered = [p for p in dev_tools_products if p.get('upvotes', 0) >= min_upvotes]
        
        # Sort by upvotes and limit results
        sorted_products = sorted(upvote_filtered, key=lambda x: x.get('upvotes', 0), reverse=True)
        result = sorted_products[:max_products]
        
        self.logger.info(f"Collected {len(result)} Product Hunt products")
        return result
        
    def _get_weekly_products(self) -> List[Dict[str, Any]]:
        """Scrape Product Hunt for weekly top products."""
        url = f"{self.base_url}/topics/developer-tools"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Extract the __NEXT_DATA__ JSON to get the products data
            # This is more reliable than scraping the HTML directly
            match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
            if not match:
                self.logger.error("Could not find Product Hunt data in page")
                return []
                
            json_data = json.loads(match.group(1))
            
            # Navigate through the JSON structure to find products
            try:
                posts = json_data.get('props', {}).get('apolloState', {})
                
                # Extract product data from the apollo state
                products = []
                
                for key, value in posts.items():
                    if key.startswith('Post:') and isinstance(value, dict):
                        # Basic product data
                        name = value.get('name', '')
                        tagline = value.get('tagline', '')
                        url = value.get('url', '')
                        slug = value.get('slug', '')
                        votes_count = value.get('votesCount', 0)
                        comments_count = value.get('commentsCount', 0)
                        created_at = value.get('createdAt', '')
                        
                        # Skip if essential data is missing
                        if not name or not url:
                            continue
                            
                        # Create product object
                        product = {
                            'name': name,
                            'tagline': tagline,
                            'url': url,
                            'ph_url': f"https://www.producthunt.com/posts/{slug}" if slug else "",
                            'upvotes': votes_count,
                            'comments': comments_count,
                            'created_at': created_at,
                            'source': 'product_hunt'
                        }
                        
                        products.append(product)
                
                return products
                
            except Exception as e:
                self.logger.error(f"Error parsing Product Hunt data: {str(e)}")
                return []
            
        except Exception as e:
            self.logger.error(f"Error scraping Product Hunt: {str(e)}")
            return []
    
    def _filter_dev_tools(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter products for developer tools.
        Note: Since we're already on the developer-tools topic page,
        most products should already be dev tools related.
        """
        # Dev tools keywords for additional filtering
        dev_keywords = [
            'developer', 'dev tool', 'sdk', 'api', 'library', 'framework',
            'cli', 'command line', 'devops', 'tooling', 'infrastructure',
            'code', 'coding', 'programmer', 'github', 'git', 'repository',
            'deployment', 'continuous', 'integration', 'testing', 'debugging'
        ]
        
        dev_tools = []
        
        for product in products:
            name = product.get('name', '').lower()
            tagline = product.get('tagline', '').lower()
            
            # Check if product description contains dev tool keywords
            if any(keyword.lower() in name or keyword.lower() in tagline for keyword in dev_keywords):
                dev_tools.append(product)
                
        return dev_tools
        
    def match_with_github_repo(self, product: Dict[str, Any]) -> Optional[str]:
        """
        Try to find a GitHub repo URL from the product data.
        Returns the GitHub repo full name or None if not found.
        """
        url = product.get('url', '')
        
        # Direct GitHub URLs
        if 'github.com' in url:
            match = re.search(r'github\.com/([^/]+/[^/]+)', url)
            if match:
                return match.group(1)
        
        # For non-GitHub URLs, we would need to:
        # 1. Visit the product URL
        # 2. Look for GitHub links in the page
        # 3. Extract repo name from those links
        
        # This is more intensive and would be a good enhancement for later
        return None
