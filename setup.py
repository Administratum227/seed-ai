"""
SEED AI Framework Installation Configuration
-----------------------------------------
Handles package installation and dependency management.
"""

from setuptools import setup, find_packages
from seed.install.commands import CustomInstallCommand, CustomDevelopCommand

setup(
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    }
)