"""Custom Installation Commands

Provides custom setuptools commands for installation and development.
"""

from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info
import logging

from .installer import install_seed_environment

logger = logging.getLogger(__name__)

class CustomInstallCommand(install):
    """Custom installation command with environment setup."""
    
    def run(self):
        """Run the installation process."""
        # Perform standard installation
        install.run(self)
        
        # Setup SEED environment
        logger.info("Setting up SEED environment...")
        try:
            install_seed_environment()
            logger.info("SEED environment setup complete")
        except Exception as e:
            logger.error(f"Environment setup failed: {e}")
            raise

class CustomDevelopCommand(develop):
    """Custom development installation command."""
    
    def run(self):
        """Run the development installation process."""
        # Perform standard development installation
        develop.run(self)
        
        # Setup SEED environment
        logger.info("Setting up SEED development environment...")
        try:
            install_seed_environment()
            logger.info("SEED development environment setup complete")
        except Exception as e:
            logger.error(f"Development environment setup failed: {e}")
            raise