"""
Authentication module for Databricks MCP server using Azure service principal.

This module handles Azure AD authentication for service principals to access
Databricks APIs, replacing the Personal Access Token (PAT) approach.
"""

import asyncio
import logging
import time
from typing import Dict, Optional
import aiohttp
from .config import settings

logger = logging.getLogger(__name__)


class ServicePrincipalAuth:
    """
    Handles Azure service principal authentication for Databricks.
    
    This class manages OAuth 2.0 token acquisition and refresh using
    Azure AD service principal credentials.
    """
    
    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._token_lock = asyncio.Lock()
        
    async def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token for Databricks API calls
            
        Raises:
            Exception: If authentication fails
        """
        async with self._token_lock:
            # Check if we have a valid token
            if self._access_token and time.time() < self._token_expires_at - 300:  # 5 min buffer
                return self._access_token
            
            # Need to get a new token
            logger.info("Acquiring new access token from Azure AD")
            await self._acquire_token()
            
            if not self._access_token:
                raise Exception("Failed to acquire access token")
                
            return self._access_token
    
    async def _acquire_token(self) -> None:
        """
        Acquire a new access token from Azure AD using service principal credentials.
        """
        # Azure AD token endpoint
        token_url = f"https://login.microsoftonline.com/{settings.DATABRICKS_TENANT_ID}/oauth2/v2.0/token"
        
        # OAuth 2.0 client credentials flow
        data = {
            "grant_type": "client_credentials",
            "client_id": settings.DATABRICKS_CLIENT_ID,
            "client_secret": settings.DATABRICKS_CLIENT_SECRET,
            "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"  # Databricks scope
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=data, headers=headers) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self._access_token = token_data["access_token"]
                        expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
                        self._token_expires_at = time.time() + expires_in
                        
                        logger.info(f"Successfully acquired access token, expires in {expires_in} seconds")
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to acquire token: {response.status} - {error_text}")
                        raise Exception(f"Token acquisition failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error during token acquisition: {str(e)}")
            raise
    
    async def get_api_headers(self) -> Dict[str, str]:
        """
        Get headers for Databricks API requests with authentication.
        
        Returns:
            Dictionary of headers including Authorization header
        """
        access_token = await self.get_access_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }


# Global authentication instance
auth = ServicePrincipalAuth()


async def get_authenticated_headers() -> Dict[str, str]:
    """
    Convenience function to get authenticated headers.
    
    Returns:
        Dictionary of headers for Databricks API requests
    """
    return await auth.get_api_headers()
