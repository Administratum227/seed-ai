"""
API Integration Manager for SEED
------------------------------
Manages connections and interactions with external APIs including Brave Search 
and GitHub. Provides a unified interface for API operations with proper error
handling and rate limiting.
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
import aiohttp
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from ratelimit import limits, sleep_and_retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APICredentials:
    """Stores API credentials and configuration."""
    brave_api_key: str
    github_token: str
    
    @classmethod
    def from_env(cls) -> 'APICredentials':
        """Create credentials from environment variables."""
        brave_key = os.getenv('BRAVE_API_KEY')
        github_token = os.getenv('GITHUB_TOKEN')
        
        if not brave_key or not github_token:
            raise ValueError(
                "Missing required environment variables: "
                "BRAVE_API_KEY and/or GITHUB_TOKEN"
            )
        
        return cls(
            brave_api_key=brave_key,
            github_token=github_token
        )

class RateLimiter:
    """Manages API rate limiting."""
    
    def __init__(self, calls: int, period: int):
        self.calls = calls
        self.period = period
        self.timestamps: List[datetime] = []
    
    async def acquire(self):
        """Acquire a rate limit token."""
        now = datetime.now()
        
        # Remove old timestamps
        self.timestamps = [
            ts for ts in self.timestamps
            if now - ts < timedelta(seconds=self.period)
        ]
        
        if len(self.timestamps) >= self.calls:
            oldest = min(self.timestamps)
            sleep_time = (oldest + timedelta(seconds=self.period) - now).total_seconds()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.timestamps.append(now)

class APIManager:
    """
    Manages external API interactions with proper rate limiting and error handling.
    
    Features:
    - Credential management
    - Rate limiting
    - Error handling
    - Response caching
    - Retry logic
    """
    
    def __init__(self, credentials: APICredentials):
        self.credentials = credentials
        self.session = aiohttp.ClientSession()
        
        # Configure rate limiters
        self.brave_limiter = RateLimiter(calls=60, period=60)  # 60 calls per minute
        self.github_limiter = RateLimiter(calls=5000, period=3600)  # 5000 calls per hour
        
        # Initialize response cache
        self.cache: Dict[str, Any] = {}
    
    async def close(self):
        """Close the API manager and cleanup resources."""
        await self.session.close()
    
    async def brave_search(
        self,
        query: str,
        count: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Perform a Brave search query.
        
        Args:
            query: Search query string
            count: Number of results (1-20)
            offset: Results offset for pagination
            
        Returns:
            Search results dictionary
        """
        await self.brave_limiter.acquire()
        
        headers = {
            'X-Subscription-Token': self.credentials.brave_api_key,
            'Accept': 'application/json'
        }
        
        params = {
            'q': query,
            'count': min(count, 20),
            'offset': offset
        }
        
        cache_key = f"brave_search:{query}:{count}:{offset}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            async with self.session.get(
                'https://api.search.brave.com/res/v1/web/search',
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    self.cache[cache_key] = results
                    return results
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Brave search error: {response.status} - {error_text}"
                    )
                    raise APIError(
                        f"Brave search failed: {response.status}"
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"Brave search request failed: {str(e)}")
            raise APIError(f"Brave search request failed: {str(e)}")
    
    async def github_operation(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Any:
        """
        Perform a GitHub API operation.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            API response data
        """
        await self.github_limiter.acquire()
        
        headers = {
            'Authorization': f'token {self.credentials.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com/{endpoint.lstrip("/")}'
        
        try:
            async with self.session.request(
                method,
                url,
                headers=headers,
                **kwargs
            ) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(
                        f"GitHub API error: {response.status} - {error_text}"
                    )
                    raise APIError(
                        f"GitHub operation failed: {response.status}"
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"GitHub request failed: {str(e)}")
            raise APIError(f"GitHub request failed: {str(e)}")
    
    async def create_github_repo(
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
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": True
        }
        
        return await self.github_operation(
            'POST',
            '/user/repos',
            json=data
        )
    
    async def push_to_github(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Push content to a GitHub repository.
        
        Args:
            repo: Repository name
            path: File path in repository
            content: File content
            message: Commit message
            branch: Target branch
            
        Returns:
            Push operation result data
        """
        import base64
        
        # Get current file (if exists) to get SHA
        try:
            current_file = await self.github_operation(
                'GET',
                f'/repos/{repo}/contents/{path}'
            )
            sha = current_file.get('sha')
        except APIError:
            sha = None
        
        data = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch
        }
        
        if sha:
            data["sha"] = sha
        
        return await self.github_operation(
            'PUT',
            f'/repos/{repo}/contents/{path}',
            json=data
        )

class APIError(Exception):
    """Raised when an API operation fails."""
    pass