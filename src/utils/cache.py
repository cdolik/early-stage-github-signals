"""
Cache utilities for the Early Stage GitHub Signals platform.
"""
import os
import json
import time
import hashlib
from typing import Any, Dict, Optional, Union


class Cache:
    """
    Simple file-based caching system to reduce API calls.
    """
    def __init__(self, cache_dir: str = None, ttl: int = 86400, enabled: bool = None):
        """
        Initialize the cache system.
        
        Args:
            cache_dir: Directory to store cache files. If None, uses config.
            ttl: Time to live in seconds for cache entries (default: 24 hours)
            enabled: Whether caching is enabled (default: True or from config)
        """
        from .config import Config
        config = Config()
        
        # Allow explicitly setting enabled status through parameter
        if enabled is not None:
            self.cache_enabled = enabled
        else:
            self.cache_enabled = config.get('cache.enabled', True)
        
        if cache_dir is None:
            # Get cache directory from config
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_dir, "../.."))
            cache_dir = config.get('cache.directory', os.path.join(project_root, "data/cache"))
            
        self.cache_dir = cache_dir
        self.ttl = config.get('cache.ttl', ttl)
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """
        Get the file path for a cache key.
        
        Args:
            key: The cache key
            
        Returns:
            The file path for the cache entry
        """
        # Hash the key to create a filename
        hashed_key = hashlib.md5(key.encode('utf-8')).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        if not self.cache_enabled:
            return None
            
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                cache_entry = json.load(f)
                
            # Check if the cache entry has expired
            timestamp = cache_entry.get('timestamp', 0)
            if time.time() - timestamp > self.ttl:
                # Cache expired, remove it
                os.remove(cache_path)
                return None
                
            return cache_entry.get('data')
        except (json.JSONDecodeError, IOError):
            # Invalid cache entry, remove it
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
        """
        if not self.cache_enabled:
            return
            
        cache_path = self._get_cache_path(key)
        
        try:
            cache_entry = {
                'timestamp': time.time(),
                'data': value
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_entry, f)
        except IOError:
            # If we can't write to the cache, just continue without caching
            pass
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate a cache entry.
        
        Args:
            key: The cache key
            
        Returns:
            True if the entry was found and invalidated, False otherwise
        """
        if not self.cache_enabled:
            return False
            
        cache_path = self._get_cache_path(key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except IOError:
                pass
                
        return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            The number of entries cleared
        """
        if not self.cache_enabled or not os.path.exists(self.cache_dir):
            return 0
            
        count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
                except IOError:
                    continue
                    
        return count
