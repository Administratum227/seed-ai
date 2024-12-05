"""SEED Configuration Management

Handles creation and management of SEED configuration files.
"""

from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

def create_default_config() -> None:
    """Create default SEED configuration file."""
    config_dir = Path.home() / '.seed' / 'config'
    config_file = config_dir / 'config.yaml'
    
    if config_file.exists():
        logger.info("Configuration file already exists")
        return
    
    config = {
        'version': '0.1.0',
        'runtime': {
            'max_agents': 10,
            'task_concurrency': 5,
            'log_level': 'INFO'
        },
        'api': {
            'brave_api_key': '',  # Set via environment
            'github_token': ''     # Set via environment
        },
        'agents': {
            'default_capabilities': [
                'basic_reasoning',
                'task_planning'
            ],
            'max_memory_mb': 1024,
            'startup_timeout_sec': 30
        },
        'dashboard': {
            'port': 8501,
            'theme': 'dark',
            'auto_launch': True
        }
    }
    
    try:
        with open(config_file, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
        logger.info(f"Created default configuration at {config_file}")
    except Exception as e:
        logger.error(f"Failed to create configuration: {e}")
        raise