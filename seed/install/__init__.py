"""SEED Installation System

Handles package installation, dependency management, and environment setup.
"""

from .installer import install_seed_environment
from .config import create_default_config

__all__ = ['install_seed_environment', 'create_default_config']