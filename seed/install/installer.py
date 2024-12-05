"""SEED Installation Manager

Manages the installation process including system dependencies and environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path
import logging
from typing import List, Optional

from .config import create_default_config

logger = logging.getLogger(__name__)

def install_seed_environment():
    """Set up the complete SEED environment."""
    ensure_directories()
    if sys.platform == 'darwin':
        setup_macos()
    create_default_config()

def ensure_directories() -> None:
    """Create necessary SEED directories."""
    seed_home = Path.home() / '.seed'
    directories = [
        seed_home / 'config',
        seed_home / 'data',
        seed_home / 'cache',
        seed_home / 'logs',
        seed_home / 'agents',
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def setup_macos() -> None:
    """Set up macOS-specific dependencies."""
    if not check_homebrew():
        install_homebrew()
    update_homebrew()
    install_brew_dependencies()

def check_homebrew() -> bool:
    """Check if Homebrew is installed."""
    try:
        subprocess.run(['brew', '--version'], 
                      check=True, 
                      capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_homebrew() -> None:
    """Install Homebrew package manager."""
    logger.info("Installing Homebrew...")
    script_url = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
    cmd = f'/bin/bash -c "$(curl -fsSL {script_url})"'
    try:
        subprocess.run(cmd, shell=True, check=True)
        logger.info("Homebrew installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install Homebrew: {e}")
        raise

def update_homebrew() -> None:
    """Update Homebrew and formulae."""
    logger.info("Updating Homebrew...")
    try:
        subprocess.run(['brew', 'update'], check=True)
        logger.info("Homebrew updated successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to update Homebrew: {e}")
        raise

def install_brew_dependencies() -> None:
    """Install required Homebrew packages."""
    dependencies = [
        'python@3.9',
        'openssl',
        'sqlite',
        'git',
    ]
    
    logger.info("Installing system dependencies...")
    for dep in dependencies:
        try:
            subprocess.run(['brew', 'install', dep], check=True)
            logger.info(f"Installed {dep}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {dep}: {e}")
            raise