"""
Brave Search API integration for SEED.

Provides search capabilities using the Brave Search API, with features for
result caching, rate limiting, and error handling.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path

from .base import APIProvider, APIError
from .config import APIConfig

class SearchProvider(APIProvider):
    """
    Brave Search API integration with caching and rate limiting.
    
    Features:
    - Configurable result caching
    - Automatic rate limiting
    - Error handling and retries
    - Result parsing and normalization
    """
    
    def __init__(self, config: APIConfig):
        super().__init__()
        self.config = config
        self.base_url = "https://api.search.brave.com/res/v1"
        
        # Set up caching directory
        self.cache_dir = config.cache_dir / "search"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    async def validate_credentials(self) -> bool:
        """Verify that the API key is valid."""
        try:
            # Perform a minimal test search
            await self.search("test", count=1)
            return True
        except APIError:
            return False
    
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
        # Validate parameters
        count = min(max(1, count), 20)  # Ensure count is between 1 and 20
        
        # Check cache first if enabled
        if use_cache:
            cached_results = await self._get_cached_results(
                query, count, offset
            )
            if cached_results:
                return cached_results
        
        # Prepare request
        headers = {
            "X-Subscription-Token": self.config.brave_api_key,
            "Accept": "application/json",
        }
        
        params = {
            "q": query,
            "count": count,
            "offset": offset
        }
        
        # Make request
        try:
            response = await self._make_request(
                "GET",
                f"{self.base_url}/web/search",
                headers=headers,
                params=params
            )
            
            # Parse and normalize results
            normalized_results = self._normalize_results(response)
            
            # Cache results if enabled
            if use_cache:
                await self._cache_results(
                    query, count, offset, normalized_results
                )
            
            return normalized_results
            
        except APIError as e:
            self.logger.error(f"Search failed for query '{query}': {str(e)}")
            raise
    
    async def _get_cached_results(
        self,
        query: str,
        count: int,
        offset: int
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached search results if available and not expired.
        
        Args:
            query: Original search query
            count: Number of results requested
            offset: Pagination offset
            
        Returns:
            Cached results if available and fresh, None otherwise
        """
        cache_file = self._get_cache_path(query, count, offset)
        
        if not cache_file.exists():
            return None
        
        try:
            # Read cache file
            data = json.loads(cache_file.read_text())
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(data["cached_at"])
            if datetime.now() - cached_time > timedelta(
                seconds=self.config.max_cache_age
            ):
                return None
            
            return data["results"]
            
        except Exception as e:
            self.logger.warning(f"Error reading cache: {str(e)}")
            return None
    
    async def _cache_results(
        self,
        query: str,
        count: int,
        offset: int,
        results: Dict[str, Any]
    ) -> None:
        """
        Cache search results for future use.
        
        Args:
            query: Original search query
            count: Number of results
            offset: Pagination offset
            results: Search results to cache
        """
        cache_file = self._get_cache_path(query, count, offset)
        
        cache_data = {
            "cached_at": datetime.now().isoformat(),
            "query": query,
            "count": count,
            "offset": offset,
            "results": results
        }
        
        try:
            cache_file.write_text(json.dumps(cache_data))
        except Exception as e:
            self.logger.warning(f"Error writing cache: {str(e)}")
    
    def _get_cache_path(self, query: str, count: int, offset: int) -> Path:
        """Generate cache file path for given search parameters."""
        # Create a unique cache key
        cache_key = f"{query}_{count}_{offset}".encode()
        filename = f"{hash(cache_key)}.json"
        return self.cache_dir / filename
    
    def _normalize_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize raw API results into a consistent format.
        
        Extracts and structures the most relevant information from
        the raw API response.
        
        Args:
            raw_results: Raw API response data
            
        Returns:
            Normalized results dictionary
        """
        results = []
        
        for item in raw_results.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "published": item.get("published", ""),
                "language": item.get("language", "")
            })
        
        return {
            "query": raw_results.get("query", ""),
            "total_results": raw_results.get("web", {}).get("total", 0),
            "results": results,
            "time_taken": raw_results.get("time_taken", 0)
        }