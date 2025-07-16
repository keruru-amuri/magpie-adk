"""
Base API client for Databricks operations.

Provides common functionality for all Databricks API clients including
authentication, error handling, and HTTP operations.
"""

import asyncio
import logging
from typing import Any, Dict, Optional
import aiohttp
from mcp_servers.databricks.auth import get_authenticated_headers
from mcp_servers.databricks.config import get_databricks_api_url

logger = logging.getLogger(__name__)


class DatabricksAPIError(Exception):
    """Custom exception for Databricks API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class BaseDatabricksClient:
    """
    Base client for Databricks API operations.
    
    Provides common functionality including authentication, error handling,
    and HTTP operations that can be used by specific API clients.
    """
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Databricks API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT)
            params: Query parameters
            
        Returns:
            Response data as dictionary
            
        Raises:
            DatabricksAPIError: If the request fails
        """
        url = get_databricks_api_url(endpoint)
        headers = await get_authenticated_headers()
        session = await self._get_session()
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params
            ) as response:
                response_text = await response.text()
                
                if response.status >= 400:
                    try:
                        error_data = await response.json() if response_text else {}
                    except:
                        error_data = {"message": response_text}
                    
                    error_message = error_data.get("message", f"HTTP {response.status}")
                    logger.error(f"API request failed: {error_message}")
                    raise DatabricksAPIError(
                        message=error_message,
                        status_code=response.status,
                        response_data=error_data
                    )
                
                # Handle empty responses
                if not response_text:
                    return {}
                
                try:
                    return await response.json()
                except:
                    # If response is not JSON, return as text
                    return {"response": response_text}
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise DatabricksAPIError(f"HTTP client error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
            raise DatabricksAPIError(f"Unexpected error: {str(e)}")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request."""
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request."""
        return await self._make_request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self._make_request("PUT", endpoint, data=data)
    
    async def delete(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self._make_request("DELETE", endpoint, data=data)
