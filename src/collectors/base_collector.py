"""
Base collector module for data collection classes.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..utils import Config, Cache, setup_logger


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    
    This class defines the interface that all collectors must implement
    and provides common functionality like configuration access, caching, and logging.
    """
    
    def __init__(self, config=None, cache=None):
        """
        Initialize the collector with configuration, cache and logger.
        
        Args:
            config: Configuration manager (optional)
            cache: Cache manager (optional)
        """
        self.config = config if config is not None else Config()
        self.cache = cache if cache is not None else Cache()
        self.logger = setup_logger(self.__class__.__name__)
        
    @abstractmethod
    def collect(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Collect data from the source.
        
        Args:
            **kwargs: Additional parameters specific to the collector
            
        Returns:
            List of collected data items
        """
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the collector.
        
        Returns:
            The collector name
        """
        pass
        
    def _get_cache_key(self, **kwargs: Any) -> str:
        """
        Generate a cache key for the collector based on parameters.
        
        Args:
            **kwargs: Parameters used for collecting data
            
        Returns:
            A cache key string
        """
        collector_name = self.get_name()
        # Sort kwargs for consistent cache keys
        sorted_args = sorted(f"{k}={v}" for k, v in kwargs.items())
        args_str = ",".join(sorted_args)
        return f"{collector_name}:{args_str}"
        
    def _get_from_cache(self, **kwargs: Any) -> Optional[List[Dict[str, Any]]]:
        """
        Try to get data from cache.
        
        Args:
            **kwargs: Parameters used for collecting data
            
        Returns:
            Cached data or None if not available
        """
        cache_key = self._get_cache_key(**kwargs)
        return self.cache.get(cache_key)
        
    def _save_to_cache(self, data: List[Dict[str, Any]], **kwargs: Any) -> None:
        """
        Save data to cache.
        
        Args:
            data: The data to cache
            **kwargs: Parameters used for collecting data
        """
        cache_key = self._get_cache_key(**kwargs)
        self.cache.set(cache_key, data)
        
    def get_data(self, use_cache: bool = True, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Get data, either from cache or by collecting it.
        
        Args:
            use_cache: Whether to use cached data if available
            **kwargs: Additional parameters specific to the collector
            
        Returns:
            List of data items
        """
        if use_cache:
            cached_data = self._get_from_cache(**kwargs)
            if cached_data is not None:
                self.logger.info(f"Using cached data for {self.get_name()}")
                return cached_data
                
        self.logger.info(f"Collecting data from {self.get_name()}")
        data = self.collect(**kwargs)
        self._save_to_cache(data, **kwargs)
        return data
