"""Core API Manager Implementation

Implements the central API management system for coordinating
external service integrations.
"""

import asyncio
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from ..config import APIConfig
from ..search import SearchProvider
from ..github import GitHubProvider
from ..base import APIError

class APIManager:
    """Central manager for all external API integrations."""
    
    def __init__(self, config: APIConfig):
        self.config = config
        self.logger = logging.getLogger("seed.api_manager")
        
        # Initialize providers
        self.search = SearchProvider(config)
        self.github = GitHubProvider(config)
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize and verify all API providers."""
        if self._initialized:
            return
            
        try:
            await self.search.initialize()
            await self.github.initialize()
            
            if not await self.search.validate_credentials():
                raise APIError("Invalid search credentials")
            if not await self.github.validate_credentials():
                raise APIError("Invalid GitHub credentials")
                
            self._initialized = True
            self.logger.info("API Manager initialized")
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise APIError(f"Initialization failed: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources and connections."""
        await self.search.cleanup()
        await self.github.cleanup()
        self._initialized = False
    
    async def ensure_initialized(self) -> None:
        """Ensure manager is initialized."""
        if not self._initialized:
            await self.initialize()