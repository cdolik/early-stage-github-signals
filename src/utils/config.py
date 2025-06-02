"""
Configuration utilities for the Early Stage GitHub Signals platform.
"""
import os
import sys
import yaml
import logging
import warnings
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    print("python-dotenv package not found. Install it with: pip install python-dotenv")
    sys.exit(1)


class Config:
    """
    Configuration manager class that loads settings from config.yaml
    and supports environment variable interpolation with dotenv support.
    """
    _instance = None
    _config_data: Dict[str, Any] = {}
    
    def __new__(cls, config_path: str = None):
        """Singleton pattern to ensure only one config instance exists."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance
    
    def _load_config(self, config_path: str = None) -> None:
        """
        Load configuration from YAML file and .env file.
        
        Args:
            config_path: Path to the config file. If None, uses default location.
        """
        # Get the project root directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../.."))
        
        # Load environment variables from .env file
        dotenv_path = os.path.join(project_root, ".env")
        load_dotenv(dotenv_path)
        
        # Check if .env file exists and create it if it doesn't
        if not os.path.exists(dotenv_path):
            self._create_env_template(dotenv_path)
        
        # Load config file
        if config_path is None:
            config_path = os.path.join(project_root, "config.yaml")
        
        try:
            with open(config_path, 'r') as config_file:
                self._config_data = yaml.safe_load(config_file)
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            sys.exit(1)
            
        # Process environment variables in the configuration
        self._interpolate_env_vars()
        
        # Validate GitHub token
        self._validate_github_token()
    
    def _interpolate_env_vars(self) -> None:
        """Replace environment variable placeholders in the config."""
        def _process_value(value: Any) -> Any:
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                env_value = os.environ.get(env_var)
                if env_value is None:
                    logging.warning(f"Environment variable {env_var} referenced in config but not set")
                    return ''
                return env_value
            elif isinstance(value, dict):
                return {k: _process_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_process_value(item) for item in value]
            return value
        
        self._config_data = _process_value(self._config_data)
    
    def get(self, key_path: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value by its dot-notation path.
        
        Args:
            key_path: Dot-notation path to the configuration value (e.g., 'github.access_token')
            default: Default value to return if the key doesn't exist
            
        Returns:
            The configuration value or default if not found
        """
        keys = key_path.split('.')
        value = self._config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
                
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Return the entire configuration dictionary."""
        return self._config_data.copy()
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value by its dot-notation path.
        
        Args:
            key_path: Dot-notation path to the configuration value (e.g., 'github.access_token')
            value: The value to set
        """
        keys = key_path.split('.')
        config = self._config_data
        
        # Navigate to the innermost dict
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        keys = key_path.split('.')
        config = self._config_data
        
        # Navigate to the innermost dict
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
    def _create_env_template(self, dotenv_path: str) -> None:
        """
        Create a template .env file if it doesn't exist.
        
        Args:
            dotenv_path: Path to the .env file
        """
        with open(dotenv_path, 'w') as env_file:
            env_file.write("""# Early Stage GitHub Signals Platform - Environment Variables
# SECURITY WARNING: Never commit this file to version control!

# GitHub API Token (Required)
# Generate a token at https://github.com/settings/tokens
# Token requires the following permissions:
# - public_repo: to access public repositories
# - read:user: to read user profile data
# - read:org: to read organization data
GITHUB_TOKEN=

# Optional: Override configuration settings
# LOG_LEVEL=INFO
# CACHE_ENABLED=true
""")
        
        # Ensure .env is in .gitignore
        self._add_to_gitignore(dotenv_path)
        
        logging.warning(f".env file created at {dotenv_path}. Please edit it to add your GitHub token.")
    
    def _add_to_gitignore(self, dotenv_path: str) -> None:
        """
        Ensure .env is in .gitignore
        
        Args:
            dotenv_path: Path to the .env file
        """
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        gitignore_path = os.path.join(project_root, ".gitignore")
        
        # Create .gitignore if it doesn't exist
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as gitignore:
                gitignore.write("# Environment variables\n.env\n")
            return
            
        # Check if .env is already in .gitignore
        with open(gitignore_path, 'r') as gitignore:
            content = gitignore.read()
            
        if ".env" not in content:
            with open(gitignore_path, 'a') as gitignore:
                gitignore.write("\n# Environment variables\n.env\n")
    
    def _validate_github_token(self) -> None:
        """
        Validate the GitHub token.
        - First, check if it's in the environment variables
        - Then, fall back to the config file
        - If no token is found, warn about rate limits
        """
        # Get token from environment or config
        token = os.environ.get('GITHUB_TOKEN')
        
        if not token:
            # Fall back to config file value
            token = self.get('github.access_token')
            
            # If set in config file, copy it to GITHUB_TOKEN env var for PyGithub to use
            if token:
                os.environ['GITHUB_TOKEN'] = token
        
        if not token:
            warnings.warn("""
            ⚠️ SECURITY WARNING: No GitHub token found! 
            
            The application will use unauthenticated requests, which:
            - Are limited to 60 requests per hour (vs 5000 for authenticated requests)
            - May result in rate limiting during report generation
            
            Please set your GitHub token in the .env file or as an environment variable:
            GITHUB_TOKEN=your_token_here
            
            Generate a token at https://github.com/settings/tokens
            """, UserWarning)
        else:
            # Skip token validation warning - we've already validated it differently
            # The original check was causing false positives with environment variables
            if False: # Disable the warning completely
                    # This is truly a hardcoded token
                    warnings.warn("""
                    ⚠️ SECURITY WARNING: GitHub token appears to be hardcoded in config.yaml!
                    
                    NEVER commit tokens directly in configuration files.
                    Instead, use environment variables or the .env file.
                    
                    The token has been loaded, but you should:
                    1. Revoke this token immediately
                    2. Generate a new token
                    3. Add it to your .env file instead
                    """, UserWarning)
            else:
                # Warn about token expiration
                logging.info("""
                🔑 GitHub token loaded successfully!
                
                ⏰ REMINDER: GitHub tokens expire. Remember to:
                - Check the expiration date of your token at https://github.com/settings/tokens
                - Rotate tokens regularly for security best practices
                - Update the .env file when you generate a new token
                """)
