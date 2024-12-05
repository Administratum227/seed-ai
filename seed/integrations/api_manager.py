"""
API Integration Manager
---------------------
Central manager for SEED's external API integrations.
Coordinates access to search, repository management, and other API services.
"""

import asyncio
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from .config import APIConfig
from .search import SearchProvider
from .github import GitHubProvider
from .base import APIError

class APIManager:
    """
    Manages all external API integrations for SEED.
    
    Features:
    - Centralized API configuration
    - Provider lifecycle management
    - Error handling and retries
    - Usage monitoring
    
    Usage:
        config = APIConfig.from_env()
        api_manager = APIManager(config)
        await api_manager.initialize()
        
        # Use APIs through the manager
        search_results = await api_manager.search("quantum computing")
        await api_manager.create_repository("my-project")
    """
    
    def __init__(self, config: APIConfig):
        """
        Initialize the API manager.
        
        Args:
            config: API configuration settings
        """
        self.config = config
        self.logger = logging.getLogger("seed.api_manager")
        
        # Initialize providers
        self.search = SearchProvider(config)
        self.github = GitHubProvider(config)
        
        # Track initialization state
        self._initialized = False
    
    async def initialize(self) -> None:
        """
        Initialize all API providers and verify credentials.
        
        Raises:
            APIError: If initialization or credential verification fails
        """
        if self._initialized:
            return
            
        try:
            # Initialize providers
            await self.search.initialize()
            await self.github.initialize()
            
            # Verify credentials
            search_valid = await self.search.validate_credentials()
            github_valid = await self.github.validate_credentials()
            
            if not search_valid:
                raise APIError("Invalid Brave Search API credentials")
            if not github_valid:
                raise APIError("Invalid GitHub API credentials")
            
            self._initialized = True
            self.logger.info("API Manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"API Manager initialization failed: {str(e)}")
            raise APIError(f"Initialization failed: {str(e)}")
    
    async def cleanup(self) -> None:
        """Clean up resources and close provider connections."""
        await self.search.cleanup()
        await self.github.cleanup()
        self._initialized = False
    
    async def ensure_initialized(self) -> None:
        """Ensure the manager is initialized before use."""
        if not self._initialized:
            await self.initialize()
    
    # Search Operations
    
    async def search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Perform a web search using Brave Search.
        
        Args:
            query: Search query string
            count: Number of results to return (1-20)
            offset: Pagination offset
            use_cache: Whether to use cached results if available
            
        Returns:
            Dictionary containing search results and metadata
            
        Raises:
            APIError: If the search request fails
        """
        await self.ensure_initialized()
        return await self.search.search(query, count, offset, use_cache)
    
    # GitHub Operations
    
    async def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new GitHub repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private
            
        Returns:
            Repository data dictionary
            
        Raises:
            APIError: If repository creation fails
        """
        await self.ensure_initialized()
        return await self.github.create_repository(
            name=name,
            description=description,
            private=private
        )
    
    async def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create or update a file in a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            content: File content
            message: Commit message
            branch: Target branch (optional)
            
        Returns:
            Update operation result data
            
        Raises:
            APIError: If the file update fails
        """
        await self.ensure_initialized()
        
        # Get current file SHA if it exists
        current_file = await self.github.get_file(owner, repo, path, branch)
        sha = current_file["sha"] if current_file else None
        
        return await self.github.update_file(
            owner=owner,
            repo=repo,
            path=path,
            content=content,
            message=message,
            branch=branch,
            sha=sha
        )
    
    async def create_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
        source_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new branch in a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: New branch name
            source_branch: Source branch (optional)
            
        Returns:
            Branch creation result data
            
        Raises:
            APIError: If branch creation fails
        """
        await self.ensure_initialized()
        return await self.github.create_branch(
            owner=owner,
            repo=repo,
            branch=branch,
            source_branch=source_branch
        )
    
    # Utility Methods
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics.
        
        Returns:
            Dictionary containing usage metrics for each provider
        """
        return {
            "search": {
                "requests": self.search.request_count,
                "cache_hits": self.search.cache_hits,
                "errors": self.search.error_count
            },
            "github": {
                "requests": self.github.request_count,
                "errors": self.github.error_count
            }
        }