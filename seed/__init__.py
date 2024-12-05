"""SEED Framework

Scalable Ecosystem for Evolving Digital Agents
"""

__version__ = "0.1.0"

from .dashboard.base import DashboardApp
from .cli.commands import app as cli

__all__ = ['DashboardApp', 'cli']