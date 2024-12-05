"""
SEED AI Framework Installation Configuration
-----------------------------------------
Handles package installation and dependency management, including integration
with package managers like Homebrew for system-level dependencies.
"""

import os
import sys
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

def check_homebrew():
    """Check if Homebrew is installed."""
    try:
        subprocess.run(['brew', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_homebrew():
    """Install Homebrew if not present."""
    print("Installing Homebrew...")
    homebrew_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    subprocess.run(homebrew_script, shell=True, check=True)

def update_homebrew():
    """Update Homebrew and install required system dependencies."""
    print("Updating Homebrew and installing dependencies...")
    subprocess.run(['brew', 'update'], check=True)
    
    # Install system dependencies
    dependencies = [
        'python@3.9',  # Ensure consistent Python version
        'openssl',     # For secure communications
        'sqlite',      # For local storage
        'git',         # For version control
    ]
    
    for dep in dependencies:
        subprocess.run(['brew', 'install', dep], check=True)

class CustomInstallCommand(install):
    """Custom installation command that ensures system dependencies."""
    
    def run(self):
        # Check and setup Homebrew on macOS
        if sys.platform == 'darwin':  # macOS
            if not check_homebrew():
                install_homebrew()
            update_homebrew()
        
        # Proceed with normal installation
        install.run(self)
        
        # Post-installation setup
        self.setup_seed_environment()
    
    def setup_seed_environment(self):
        """Configure SEED environment after installation."""
        from pathlib import Path
        
        # Create necessary directories
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
        
        # Create default configuration
        config_file = seed_home / 'config' / 'config.yaml'
        if not config_file.exists():
            default_config = '''
# SEED AI Framework Configuration
version: 1.0.0

# Runtime Settings
runtime:
  max_agents: 10
  task_concurrency: 5
  log_level: INFO

# API Integration
api:
  brave_api_key: ""  # Set via environment variable
  github_token: ""   # Set via environment variable

# Agent Defaults
agents:
  default_capabilities:
    - basic_reasoning
    - task_planning
  max_memory_mb: 1024
  startup_timeout_sec: 30

# Dashboard Settings
dashboard:
  port: 8501
  theme: dark
  auto_launch: true
'''
            config_file.write_text(default_config)

setup(
    name="seed-ai-framework",
    version="0.1.0",
    author="SEED AI Framework Team",
    description="Scalable Ecosystem for Evolving Digital Agents",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Administratum227/seed-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    install_requires=[
        "aiohttp>=3.8.0",
        "pyyaml>=6.0",
        "rich>=10.0.0",
        "typer>=0.4.0",
        "textual>=0.1.18",
        "cryptography>=36.0.0",
        "pydantic>=1.9.0",
        "anthropic>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "seed=seed.cli:main",
        ],
    },
    cmdclass={
        'install': CustomInstallCommand,
    },
)
