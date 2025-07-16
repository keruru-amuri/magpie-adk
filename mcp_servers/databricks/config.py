"""
Configuration settings for the centralized Databricks MCP server.

This configuration supports Azure service principal authentication
instead of Personal Access Token (PAT) authentication.
"""

import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings

# Import dotenv if available, but don't require it
try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    if load_dotenv():
        print("Successfully loaded .env file for Databricks MCP server")
    else:
        print("No .env file found for Databricks MCP server")
except ImportError:
    print("WARNING: python-dotenv not found, relying on environment variables.")

# Version
VERSION = "1.0.0"


class DatabricksSettings(BaseSettings):
    """Settings for Databricks MCP server with service principal authentication."""
    
    # Databricks workspace configuration
    DATABRICKS_WORKSPACE_URL: str = os.environ.get("DATABRICKS_WORKSPACE_URL", "")
    
    # Azure service principal authentication
    DATABRICKS_CLIENT_ID: str = os.environ.get("DATABRICKS_CLIENT_ID", "")
    DATABRICKS_CLIENT_SECRET: str = os.environ.get("DATABRICKS_CLIENT_SECRET", "")
    DATABRICKS_TENANT_ID: str = os.environ.get("DATABRICKS_TENANT_ID", "")
    
    # Optional warehouse ID for SQL operations
    DATABRICKS_WAREHOUSE_ID: Optional[str] = os.environ.get("DATABRICKS_WAREHOUSE_ID")
    
    # Server configuration
    SERVER_HOST: str = os.environ.get("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.environ.get("SERVER_PORT", "8000"))
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    
    # Version
    VERSION: str = VERSION

    @field_validator("DATABRICKS_WORKSPACE_URL")
    def validate_workspace_url(cls, v: str) -> str:
        """Validate Databricks workspace URL."""
        if not v:
            raise ValueError("DATABRICKS_WORKSPACE_URL is required")
        if not v.startswith(("https://", "http://")):
            raise ValueError("DATABRICKS_WORKSPACE_URL must start with http:// or https://")
        return v.rstrip("/")

    @field_validator("DATABRICKS_CLIENT_ID")
    def validate_client_id(cls, v: str) -> str:
        """Validate service principal client ID."""
        if not v:
            raise ValueError("DATABRICKS_CLIENT_ID is required for service principal authentication")
        return v

    @field_validator("DATABRICKS_CLIENT_SECRET")
    def validate_client_secret(cls, v: str) -> str:
        """Validate service principal client secret."""
        if not v:
            raise ValueError("DATABRICKS_CLIENT_SECRET is required for service principal authentication")
        return v

    @field_validator("DATABRICKS_TENANT_ID")
    def validate_tenant_id(cls, v: str) -> str:
        """Validate Azure tenant ID."""
        if not v:
            raise ValueError("DATABRICKS_TENANT_ID is required for service principal authentication")
        return v

    @field_validator("DATABRICKS_WAREHOUSE_ID")
    def validate_warehouse_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate warehouse ID format if provided."""
        if v and len(v) < 10:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Warehouse ID '{v}' seems unusually short")
        return v

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Create global settings instance
settings = DatabricksSettings()


def get_databricks_api_url(endpoint: str) -> str:
    """
    Construct the full Databricks API URL.
    
    Args:
        endpoint: The API endpoint path, e.g., "/api/2.0/clusters/list"
        
    Returns:
        Full URL to the Databricks API endpoint
    """
    # Ensure endpoint starts with a slash
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    return f"{settings.DATABRICKS_WORKSPACE_URL}{endpoint}"
