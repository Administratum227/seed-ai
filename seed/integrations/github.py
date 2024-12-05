"""GitHub API integration for SEED.

Provides repository management and code operations through the GitHub API.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
from pathlib import Path

from .base import APIProvider, APIError
from .config import APIConfig

class GitHubProvider(APIProvider):
    """
    GitHub API integration for repository and code management.
    
    Features:
    - Repository creation and management
    - File operations (create, update, delete)
    - Branch management
    - Commit handling
    """
    
    def __init__(self, config: APIConfig):
        super().__init__()
        self.config = config
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {config.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def validate_credentials(self) -> bool:
        """Verify that the GitHub token is valid."""
        try:
            await self._make_request(
                "GET",
                f"{self.base_url}/user",
                headers=self.headers
            )
            return True
        except APIError:
            return False
    
    async def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True
    ) -> Dict[str, Any]:
        """Create a new GitHub repository.
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether the repository should be private
            auto_init: Initialize with README
            
        Returns:
            Repository data dictionary
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        }
        
        try:
            return await self._make_request(
                "POST",
                f"{self.base_url}/user/repos",
                headers=self.headers,
                json=data
            )
        except APIError as e:
            self.logger.error(f"Failed to create repository: {str(e)}")
            raise
    
    async def get_file(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get file contents from a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Git reference (branch, tag, commit)
            
        Returns:
            File data dictionary
        """
        params = {}
        if ref:
            params["ref"] = ref
            
        try:
            return await self._make_request(
                "GET",
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                params=params
            )
        except APIError as e:
            if "404" in str(e):
                return None
            raise
    
    async def update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: Optional[str] = None,
        sha: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update a file in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            content: File content
            message: Commit message
            branch: Target branch
            sha: File SHA (required for updates)
            
        Returns:
            Update operation result data
        """
        data = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode()
        }
        
        if branch:
            data["branch"] = branch
        if sha:
            data["sha"] = sha
        
        try:
            return await self._make_request(
                "PUT",
                f"{self.base_url}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers,
                json=data
            )
        except APIError as e:
            self.logger.error(f"Failed to update file: {str(e)}")
            raise
    
    async def create_branch(
        self,
        owner: str,
        repo: str,
        branch: str,
        source_branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new branch in a repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: New branch name
            source_branch: Source branch (defaults to default branch)
            
        Returns:
            Branch creation result data
        """
        # Get source branch reference
        if not source_branch:
            repo_data = await self._make_request(
                "GET",
                f"{self.base_url}/repos/{owner}/{repo}",
                headers=self.headers
            )
            source_branch = repo_data["default_branch"]
        
        # Get source branch SHA
        source_ref = await self._make_request(
            "GET",
            f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{source_branch}",
            headers=self.headers
        )
        
        # Create new branch
        data = {
            "ref": f"refs/heads/{branch}",
            "sha": source_ref["object"]["sha"]
        }
        
        try:
            return await self._make_request(
                "POST",
                f"{self.base_url}/repos/{owner}/{repo}/git/refs",
                headers=self.headers,
                json=data
            )
        except APIError as e:
            self.logger.error(f"Failed to create branch: {str(e)}")
            raise