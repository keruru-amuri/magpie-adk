"""
Databricks Notebooks API client for the centralized MCP server.

This module provides API client functionality for Databricks Workspace API
notebook operations, including creating, listing, importing, exporting, and
managing notebooks.
"""

import base64
import json
import logging
from typing import Dict, List, Optional, Any, Union
from .base import BaseDatabricksClient

logger = logging.getLogger(__name__)


class NotebooksClient(BaseDatabricksClient):
    """
    Client for Databricks Workspace API notebook operations.
    
    Provides methods for managing notebooks including:
    - Listing workspace objects (notebooks, directories)
    - Creating and importing notebooks
    - Exporting notebooks in various formats
    - Getting notebook metadata
    - Creating directories
    - Deleting notebooks and directories
    """
    
    async def list_workspace_objects(
        self, 
        path: str = "/", 
        object_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List objects in a workspace directory.
        
        Args:
            path: Workspace path to list (default: root "/")
            object_type: Filter by object type (NOTEBOOK, DIRECTORY, LIBRARY, FILE)
            
        Returns:
            Dictionary containing list of workspace objects
        """
        params = {"path": path}
        if object_type:
            params["object_type"] = object_type
            
        logger.info(f"Listing workspace objects at path: {path}")
        return await self.get("/api/2.0/workspace/list", params=params)
    
    async def get_notebook_status(self, path: str) -> Dict[str, Any]:
        """
        Get metadata about a workspace object.
        
        Args:
            path: Full workspace path to the object
            
        Returns:
            Dictionary containing object metadata
        """
        params = {"path": path}
        logger.info(f"Getting status for workspace object: {path}")
        return await self.get("/api/2.0/workspace/get-status", params=params)
    
    async def export_notebook(
        self, 
        path: str, 
        format: str = "SOURCE",
        direct_download: bool = False
    ) -> Dict[str, Any]:
        """
        Export a notebook from the workspace.
        
        Args:
            path: Full workspace path to the notebook
            format: Export format (SOURCE, HTML, JUPYTER, DBC, AUTO)
            direct_download: If True, return content directly; if False, return base64 encoded
            
        Returns:
            Dictionary containing exported notebook content
        """
        params = {
            "path": path,
            "format": format,
            "direct_download": direct_download
        }
        logger.info(f"Exporting notebook: {path} in format: {format}")
        return await self.get("/api/2.0/workspace/export", params=params)
    
    async def import_notebook(
        self, 
        path: str, 
        content: str, 
        format: str = "AUTO",
        language: Optional[str] = None,
        overwrite: bool = False
    ) -> Dict[str, Any]:
        """
        Import a notebook to the workspace.
        
        Args:
            path: Target workspace path for the notebook
            content: Base64 encoded notebook content or raw content
            format: Import format (SOURCE, HTML, JUPYTER, DBC, AUTO)
            language: Programming language (SCALA, PYTHON, SQL, R)
            overwrite: Whether to overwrite existing notebook
            
        Returns:
            Dictionary containing import result
        """
        data = {
            "path": path,
            "content": content,
            "format": format,
            "overwrite": overwrite
        }
        if language:
            data["language"] = language
            
        logger.info(f"Importing notebook to: {path} with format: {format}")
        return await self.post("/api/2.0/workspace/import", data=data)
    
    async def create_notebook(
        self, 
        path: str, 
        language: str = "PYTHON",
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new notebook in the workspace.
        
        Args:
            path: Target workspace path for the new notebook
            language: Programming language (SCALA, PYTHON, SQL, R)
            content: Initial notebook content (optional)
            
        Returns:
            Dictionary containing creation result
        """
        # Create basic notebook content if none provided
        if content is None:
            if language.upper() == "PYTHON":
                content = "# Databricks notebook source\nprint('Hello, Databricks!')"
            elif language.upper() == "SQL":
                content = "-- Databricks notebook source\nSELECT 'Hello, Databricks!' as greeting"
            elif language.upper() == "SCALA":
                content = "// Databricks notebook source\nprintln(\"Hello, Databricks!\")"
            elif language.upper() == "R":
                content = "# Databricks notebook source\nprint('Hello, Databricks!')"
            else:
                content = f"# Databricks notebook source\n# Language: {language}"
        
        # Encode content as base64
        content_base64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        return await self.import_notebook(
            path=path,
            content=content_base64,
            format="SOURCE",
            language=language.upper(),
            overwrite=False
        )
    
    async def delete_notebook(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Delete a notebook or directory from the workspace.
        
        Args:
            path: Full workspace path to delete
            recursive: Whether to delete directories recursively
            
        Returns:
            Dictionary containing deletion result
        """
        data = {
            "path": path,
            "recursive": recursive
        }
        logger.info(f"Deleting workspace object: {path} (recursive: {recursive})")
        return await self.post("/api/2.0/workspace/delete", data=data)
    
    async def create_directory(self, path: str) -> Dict[str, Any]:
        """
        Create a directory in the workspace.
        
        Args:
            path: Full workspace path for the new directory
            
        Returns:
            Dictionary containing creation result
        """
        data = {"path": path}
        logger.info(f"Creating directory: {path}")
        return await self.post("/api/2.0/workspace/mkdirs", data=data)
    
    async def search_notebooks(
        self, 
        query: str, 
        max_results: int = 25,
        path_prefix: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for notebooks in the workspace.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            path_prefix: Limit search to paths starting with this prefix
            
        Returns:
            List of matching notebook objects
        """
        # Note: This is a simplified search implementation
        # In practice, you might want to use more sophisticated search
        all_objects = await self.list_workspace_objects(path=path_prefix or "/")
        
        matching_objects = []
        for obj in all_objects.get("objects", []):
            if obj.get("object_type") == "NOTEBOOK":
                # Simple text matching in path
                if query.lower() in obj.get("path", "").lower():
                    matching_objects.append(obj)
                    if len(matching_objects) >= max_results:
                        break
        
        logger.info(f"Found {len(matching_objects)} notebooks matching query: {query}")
        return matching_objects
