"""
Helper utilities for the Early Stage GitHub Signals platform.
"""
import re
import time
import datetime
from typing import Any, Dict, Optional, Union, Callable
import requests
from dateutil import parser


def format_date(date_obj: datetime.datetime) -> str:
    """
    Format a date object as YYYY-MM-DD.
    
    Args:
        date_obj: The datetime object to format
        
    Returns:
        Formatted date string
    """
    return date_obj.strftime('%Y-%m-%d')


def parse_date(date_str: str) -> datetime.datetime:
    """
    Parse a date string into a datetime object.
    
    Args:
        date_str: The date string to parse
        
    Returns:
        Parsed datetime object
    """
    return parser.parse(date_str)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string for use as a filename.
    
    Args:
        name: The name to sanitize
        
    Returns:
        Sanitized filename string
    """
    # Replace invalid characters with underscores
    return re.sub(r'[\\/*?:"<>|]', '_', name)


def rate_limited_request(
    req_func: Callable,
    max_retries: int = 3,
    base_delay: float = 2.0,
    *args: Any,
    **kwargs: Any
) -> requests.Response:
    """
    Make a rate-limited request with exponential backoff.
    
    Args:
        req_func: The request function to call (e.g., requests.get)
        max_retries: Maximum number of retries on failure
        base_delay: Base delay for exponential backoff
        *args: Arguments to pass to the request function
        **kwargs: Keyword arguments to pass to the request function
        
    Returns:
        The response object
        
    Raises:
        requests.exceptions.RequestException: If all retries fail
    """
    from .logger import setup_logger
    logger = setup_logger("rate_limiter")
    
    retries = 0
    while retries <= max_retries:
        try:
            response = req_func(*args, **kwargs)
            
            # Check for rate limiting
            if response.status_code == 403 and 'rate limit exceeded' in response.text.lower():
                if retries == max_retries:
                    raise requests.exceptions.RequestException(
                        f"Rate limit exceeded after {max_retries} retries"
                    )
                # Exponential backoff
                delay = base_delay * (2 ** retries)
                logger.warning(f"Rate limit hit. Waiting {delay} seconds before retry.")
                time.sleep(delay)
                retries += 1
                continue
                
            # Handle other response codes
            if response.status_code >= 400:
                if retries == max_retries:
                    response.raise_for_status()
                # Exponential backoff
                delay = base_delay * (2 ** retries)
                logger.warning(f"Request failed with status {response.status_code}. "
                              f"Waiting {delay} seconds before retry.")
                time.sleep(delay)
                retries += 1
                continue
                
            return response
            
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            if retries == max_retries:
                raise
                
            # Exponential backoff
            delay = base_delay * (2 ** retries)
            logger.warning(f"Request failed with error: {str(e)}. "
                          f"Waiting {delay} seconds before retry.")
            time.sleep(delay)
            retries += 1
            
    # This should not be reachable, but just in case
    raise requests.exceptions.RequestException("Request failed after max retries")
