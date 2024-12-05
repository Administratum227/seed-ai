"""SEED External API Integrations

Provides interfaces for interacting with external services and APIs.
"""

from .api_manager import APIManager, APICredentials
from .search import SearchProvider
from .github import GitHubProvider

__all__ = [
    'APIManager',
    'APICredentials',
    'SearchProvider',
    'GitHubProvider'
]