"""
Logging utilities for the Early Stage GitHub Signals platform.
"""
import os
import logging
from typing import Optional


def setup_logger(name: str = None, level: Optional[str] = None,
                log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure a logger.
    
    Args:
        name: The logger name (default is root logger)
        level: The log level (default from config)
        log_file: The log file path (default from config)
        
    Returns:
        The configured logger instance
    """
    from .config import Config
    config = Config()
    
    if name is None:
        name = 'github_signals'
        
    if level is None:
        level = config.get('logging.level', 'INFO')
        
    if log_file is None:
        log_file = config.get('logging.file', 'github_signals.log')
        
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatters and handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
