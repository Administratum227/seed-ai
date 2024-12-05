"""SEED Dashboard Interface

Provides a web-based user interface for managing SEED agents and monitoring
system status. The dashboard follows a modular design pattern for easy
extensibility.
"""

from .app import launch_dashboard

__all__ = ['launch_dashboard']