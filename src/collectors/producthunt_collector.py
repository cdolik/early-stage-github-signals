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
            self.logger.debug(f"Fetching Product Hunt data from URL: {url}")
            
            # Update headers to mimic a browser better
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.producthunt.com/'
            })
            
            response = self.session.get(url, timeout=10)
            self.logger.debug(f"Response status code: {response.status_code}")
            
            # Check for rate limiting
            if response.status_code == 429:
                self.logger.error("Rate limited by Product Hunt (429 status code)")
                return []
                
            response.raise_for_status()
            
            # Debug response
            content_length = len(response.text)
            self.logger.debug(f"Response content length: {content_length} characters")
            
            # First method: Try using the regex pattern for __NEXT_DATA__
            products = self._extract_products_next_data(response.text)
            if products:
                return products
                
            # Second method: Try using BeautifulSoup directly
            products = self._extract_products_soup(response.text)
            if products:
                return products
                
            # Third method: Try using a direct GraphQL request as a last resort
            products = self._extract_products_graphql()
            if products:
                return products
                
            # If all methods fail, return empty list
            self.logger.error("All extraction methods failed for Product Hunt")
            return []
            
        except Exception as e:
            self.logger.error(f"Error scraping Product Hunt: {str(e)}")
            return []
            
    def _extract_products_next_data(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract products from __NEXT_DATA__ script tag."""
        try:
            # Try multiple regex patterns
            patterns = [
                r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                r'<script[^>]*>window\.__NEXT_DATA__\s*=\s*(.*?);</script>'
            ]
            
            json_data = None
            for pattern in patterns:
                match = re.search(pattern, html_content, re.DOTALL)
                if match:
                    self.logger.debug(f"Found __NEXT_DATA__ with pattern: {pattern[:30]}...")
                    try:
                        json_data = json.loads(match.group(1))
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not json_data:
                self.logger.debug("Could not extract __NEXT_DATA__ JSON")
                return []
                
            # Try to navigate through the JSON structure to find products
            products = []
            try:
                # Check for apolloState pattern
                if 'props' in json_data and 'apolloState' in json_data['props']:
                    posts = json_data['props']['apolloState']
                    
                    for key, value in posts.items():
                        if key.startswith('Post:') and isinstance(value, dict):
                            # Extract product data
                            product = self._extract_product_from_post(value)
                            if product:
                                products.append(product)
                                
                # Check for pageProps pattern (newer structure)
                elif 'props' in json_data and 'pageProps' in json_data['props']:
                    page_props = json_data['props']['pageProps']
                    
                    # Try to find posts in various possible locations
                    post_locations = [
                        page_props.get('posts', []),
                        page_props.get('topic', {}).get('posts', []),
                        page_props.get('initialData', {}).get('posts', [])
                    ]
                    
                    for posts in post_locations:
                        if posts and isinstance(posts, list):
                            for post in posts:
                                product = self._extract_product_from_post(post)
                                if product:
                                    products.append(product)
                
                self.logger.debug(f"Extracted {len(products)} products from __NEXT_DATA__")
                return products
                
            except Exception as e:
                self.logger.error(f"Error parsing Product Hunt data structure: {str(e)}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in _extract_products_next_data: {str(e)}")
            return []
    
    def _extract_product_from_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract product data from a post object."""
        try:
            # Handle different post structures
            if isinstance(post, dict):
                name = post.get('name', '')
                tagline = post.get('tagline', '')
                url = post.get('url', '')
                slug = post.get('slug', '')
                votes_count = post.get('votesCount', 0)
                
                # Alternative field names
                if not name and 'title' in post:
                    name = post['title']
                if not tagline and 'description' in post:
                    tagline = post['description']
                if not url and 'website' in post:
                    url = post['website']
                if not votes_count:
                    votes_count = post.get('votes', 0) or post.get('points', 0) or post.get('upvotes', 0)
                
                # Skip if essential data is missing
                if not name or not tagline:
                    return None
                    
                # Create product object
                product = {
                    'name': name,
                    'tagline': tagline,
                    'url': url,
                    'ph_url': f"https://www.producthunt.com/posts/{slug}" if slug else "",
                    'upvotes': votes_count,
                    'comments': post.get('commentsCount', 0),
                    'created_at': post.get('createdAt', ''),
                    'source': 'product_hunt'
                }
                
                return product
        except Exception as e:
            self.logger.debug(f"Error extracting product from post: {str(e)}")
            return None
        
    def _extract_products_soup(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract products using BeautifulSoup."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            products = []
            
            # Try to find product cards
            product_cards = soup.select('.item-card, .product-card, .post-card, .ph-card')
            self.logger.debug(f"Found {len(product_cards)} potential product cards with BeautifulSoup")
            
            for card in product_cards:
                try:
                    # Try to extract product info from card
                    name_elem = card.select_one('.item-title, .product-name, .post-title, h3, h2')
                    tagline_elem = card.select_one('.item-tagline, .product-tagline, .post-tagline, .description, p')
                    votes_elem = card.select_one('.item-votes, .product-votes, .post-votes, .upvote-count, .vote-count')
                    
                    name = name_elem.text.strip() if name_elem else ''
                    tagline = tagline_elem.text.strip() if tagline_elem else ''
                    votes = votes_elem.text.strip() if votes_elem else '0'
                    
                    # Try to convert votes to int
                    try:
                        votes_count = int(''.join(filter(str.isdigit, votes)))
                    except ValueError:
                        votes_count = 0
                    
                    # Get URL
                    url = ''
                    link_elem = card.select_one('a[href*="/posts/"]')
                    if link_elem and 'href' in link_elem.attrs:
                        href = link_elem['href']
                        slug = href.split('/')[-1] if '/' in href else href
                        url = f"https://www.producthunt.com{href}"
                    
                    if name and tagline:
                        products.append({
                            'name': name,
                            'tagline': tagline,
                            'url': url,
                            'ph_url': url,
                            'upvotes': votes_count,
                            'comments': 0,
                            'source': 'product_hunt'
                        })
                except Exception as e:
                    self.logger.debug(f"Error processing card: {str(e)}")
                    continue
            
            self.logger.debug(f"Extracted {len(products)} products with BeautifulSoup")
            return products
            
        except Exception as e:
            self.logger.error(f"Error in _extract_products_soup: {str(e)}")
            return []
            
    def _extract_products_graphql(self) -> List[Dict[str, Any]]:
        """Try to extract products using Product Hunt's GraphQL API."""
        try:
            url = "https://www.producthunt.com/frontend/graphql"
            
            # GraphQL query for developer tools topics
            query = """
            query TopicPage($slug: String!) {
              topic(slug: $slug) {
                id
                name
                description
                posts(first: 20, order: RANKING) {
                  edges {
                    node {
                      id
                      name
                      tagline
                      slug
                      votesCount
                      website
                      commentsCount
                    }
                  }
                }
              }
            }
            """
            
            variables = {"slug": "developer-tools"}
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            payload = {
                "query": query,
                "variables": variables
            }
            
            self.logger.debug("Attempting GraphQL request to Product Hunt")
            response = self.session.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.logger.debug(f"GraphQL request failed with status {response.status_code}")
                return []
                
            data = response.json()
            
            if 'data' in data and 'topic' in data['data'] and 'posts' in data['data']['topic']:
                posts_data = data['data']['topic']['posts']['edges']
                
                products = []
                for edge in posts_data:
                    node = edge['node']
                    
                    product = {
                        'name': node.get('name', ''),
                        'tagline': node.get('tagline', ''),
                        'url': node.get('website', ''),
                        'ph_url': f"https://www.producthunt.com/posts/{node.get('slug', '')}",
                        'upvotes': node.get('votesCount', 0),
                        'comments': node.get('commentsCount', 0),
                        'source': 'product_hunt'
                    }
                    
                    products.append(product)
                
                self.logger.debug(f"Extracted {len(products)} products with GraphQL")
                return products
            else:
                self.logger.debug("GraphQL response didn't contain expected data structure")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in _extract_products_graphql: {str(e)}")
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
