"""API Operation Methods

Implements the core API operations supported by the manager.
"""

from typing import Dict, Any, Optional
from pathlib import Path

class APIOperations:
    """Mixin class providing API operations."""
    
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
            count: Number of results (1-20)
            offset: Results offset
            use_cache: Use cached results if available
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
            private: Whether repo should be private
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
        Update or create a file in a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            content: File content
            message: Commit message
            branch: Target branch
        """
        await self.ensure_initialized()
        
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
        Create a new branch in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: New branch name
            source_branch: Source branch
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
        """Get API usage statistics."""
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