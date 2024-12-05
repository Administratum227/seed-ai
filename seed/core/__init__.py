"""SEED Core Module

Provides essential functionality for the SEED framework including:
- Pre-flight system checks
- Basic configuration
- Common utilities
"""

from .preflight import run_checks

__all__ = ['run_checks']