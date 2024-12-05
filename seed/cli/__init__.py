"""SEED Command Line Interface

Provides a streamlined CLI for managing SEED framework operations.
"""

from .core import launch_dashboard
from .commands import app as cli

__all__ = ['launch_dashboard', 'cli']