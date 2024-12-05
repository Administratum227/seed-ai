"""Configuration management for API integrations."""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path
import yaml

@dataclass
class APIConfig:
    """API configuration settings.
    
    Attributes:
        brave_api_key: Brave Search API key
        github_token: GitHub Personal Access Token
        cache_dir: Directory for caching API responses
        max_cache_age: Maximum age of cached responses in seconds
    """
    
    brave_api_key: str
    github_token: str
    cache_dir: Path = Path.home() / '.seed' / 'cache'
    max_cache_age: int = 3600  # 1 hour
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Load configuration from environment variables."""
        required_vars = {
            'BRAVE_API_KEY': 'Brave Search API key',
            'GITHUB_TOKEN': 'GitHub Personal Access Token'
        }
        
        # Verify all required variables are present
        missing = []
        for var, desc in required_vars.items():
            if not os.getenv(var):
                missing.append(f"{desc} ({var})")
        
        if missing:
            raise ValueError(
                "Missing required environment variables: " +
                ", ".join(missing)
            )
        
        return cls(
            brave_api_key=os.getenv('BRAVE_API_KEY'),
            github_token=os.getenv('GITHUB_TOKEN')
        )
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'APIConfig':
        """Load configuration from YAML file."""
        if not config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {config_path}"
            )
        
        with open(config_path) as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
