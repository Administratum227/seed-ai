"""Configuration Management System

Provides a flexible configuration system with:
- Environment variable support
- YAML file loading
- Dynamic updates
- Validation
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import os
import yaml
from dataclasses import dataclass
import logging

from .exceptions import ConfigError

@dataclass
class ConfigValue:
    """Configuration value with metadata."""
    value: Any
    source: str  # 'default', 'file', or 'env'
    last_updated: float

class Config:
    """Configuration management system.
    
    Features:
    - Hierarchical configuration
    - Environment variable override
    - Dynamic reloading
    - Type validation
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize configuration system.
        
        Args:
            config_path: Optional path to configuration file
        """
        self._config: Dict[str, ConfigValue] = {}
        self._config_path = config_path
        self.logger = logging.getLogger("seed.config")
        
        # Load configuration
        self._load_defaults()
        if config_path:
            self._load_file(config_path)
        self._load_environment()
    
    def _load_defaults(self) -> None:
        """Load default configuration values."""
        package_dir = Path(__file__).parent.parent
        default_config = package_dir / "config" / "default_config.yaml"
        
        try:
            with open(default_config) as f:
                defaults = yaml.safe_load(f)
            self._update_config(defaults, "default")
        except Exception as e:
            self.logger.error(f"Error loading defaults: {e}")
            raise ConfigError(f"Failed to load defaults: {str(e)}")
    
    def _load_file(self, path: Path) -> None:
        """Load configuration from file.
        
        Args:
            path: Path to configuration file
        """
        try:
            with open(path) as f:
                config = yaml.safe_load(f)
            self._update_config(config, "file")
        except Exception as e:
            self.logger.error(f"Error loading config file: {e}")
            raise ConfigError(f"Failed to load config file: {str(e)}")
    
    def _load_environment(self) -> None:
        """Load configuration from environment variables."""
        # Map of config keys to environment variables
        env_map = {
            "api.brave.api_key": "BRAVE_API_KEY",
            "api.github.token": "GITHUB_TOKEN",
            "security.encryption_key": "SEED_ENCRYPTION_KEY"
        }
        
        for config_key, env_var in env_map.items():
            if env_var in os.environ:
                self.set(config_key, os.environ[env_var], "env")
    
    def _update_config(self, config: Dict[str, Any], source: str) -> None:
        """Update configuration with new values.
        
        Args:
            config: Configuration dictionary
            source: Source of configuration ('default', 'file', or 'env')
        """
        def _recurse_update(prefix: str, data: Dict[str, Any]) -> None:
            for key, value in data.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, dict):
                    _recurse_update(full_key, value)
                else:
                    self.set(full_key, value, source)
        
        _recurse_update("", config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (dot-separated)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        try:
            return self._config[key].value
        except KeyError:
            if default is not None:
                return default
            raise ConfigError(f"Configuration key not found: {key}")
    
    def set(self, key: str, value: Any, source: str) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key (dot-separated)
            value: Value to set
            source: Source of the value
        """
        import time
        self._config[key] = ConfigValue(
            value=value,
            source=source,
            last_updated=time.time()
        )
    
    def reload(self) -> None:
        """Reload configuration from file."""
        if self._config_path:
            self._load_file(self._config_path)
        self._load_environment()