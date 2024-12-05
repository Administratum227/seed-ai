"""Base classes for API integrations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime
import aiohttp
import logging

class APIProvider(ABC):
    """Base class for API service providers.
    
    Provides common functionality for API interactions including:
    - Session management
    - Error handling
    - Response validation
    - Basic rate limiting
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(f"seed.api.{self.__class__.__name__}")
    
    async def initialize(self) -> None:
        """Initialize the API provider."""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Validate that the provided credentials are valid."""
        pass
    
    async def _make_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc)
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            Response data
            
        Raises:
            APIError: If the request fails
        """
        if not self.session:
            await self.initialize()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status in (200, 201):
                    return await response.json()
                else:
                    error_text = await response.text()
                    self.logger.error(
                        f"API error: {response.status} - {error_text}"
                    )
                    raise APIError(
                        f"Request failed: {response.status}"
                    )
        except aiohttp.ClientError as e:
            self.logger.error(f"Request error: {str(e)}")
            raise APIError(f"Request failed: {str(e)}")

class APIError(Exception):
    """Raised when an API request fails."""
    pass
