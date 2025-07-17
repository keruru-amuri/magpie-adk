"""
MCP Client for Data Scientist Agent

This module provides MCP client tools that connect to the centralized
Databricks MCP server for data science operations.
"""

import asyncio
import json
import subprocess
import sys
import os
import re
from typing import Dict, Any, List, Optional
import logging
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def safe_json_loads(json_str: str, default=None) -> Any:
    """Safely parse JSON string with fallback."""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        logger.warning(f"Failed to parse JSON: {e}. String: {json_str[:100]}...")
        return default if default is not None else {}


def sanitize_for_json(data: Any) -> Any:
    """Sanitize data to ensure it can be safely serialized to JSON."""
    if isinstance(data, dict):
        return {k: sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(item) for item in data]
    elif isinstance(data, str):
        # Remove or replace problematic characters
        return data.replace('\x00', '').replace('\b', '').replace('\f', '').replace('\v', '')
    else:
        return data


class DatabricksMCPClient:
    """Client for communicating with the Databricks MCP server."""

    def __init__(self):
        self.server_process = None
        self.server_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "mcp_servers", "databricks", "server.py"
        )

    async def _cleanup_sessions(self, client):
        """Clean up any open aiohttp sessions."""
        try:
            if hasattr(client, '_session') and client._session:
                await client._session.close()
            if hasattr(client, 'session') and client.session:
                await client.session.close()
        except Exception as e:
            logger.debug(f"Session cleanup warning: {e}")
    
    async def _call_mcp_tool(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call an MCP tool on the Databricks server.

        Args:
            tool_name: Name of the MCP tool to call
            params: Parameters to pass to the tool

        Returns:
            Result from the MCP tool
        """
        try:
            # For now, we'll use the direct API clients from the MCP server
            # In a full MCP implementation, this would use the MCP protocol

            # Import the API clients directly
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            if tool_name == "list_clusters":
                from mcp_servers.databricks.api.clusters import clusters_client
                try:
                    result = await clusters_client.list_clusters()
                    return {"status": "success", "data": result}
                finally:
                    # Ensure session cleanup
                    await self._cleanup_sessions(clusters_client)
                
            elif tool_name == "get_cluster":
                from mcp_servers.databricks.api.clusters import clusters_client
                cluster_id = params.get("cluster_id") if params else None
                if not cluster_id:
                    return {"status": "error", "error": "cluster_id is required"}
                try:
                    result = await clusters_client.get_cluster(cluster_id)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(clusters_client)
                
            elif tool_name == "start_cluster":
                from mcp_servers.databricks.api.clusters import clusters_client
                cluster_id = params.get("cluster_id") if params else None
                if not cluster_id:
                    return {"status": "error", "error": "cluster_id is required"}
                result = await clusters_client.start_cluster(cluster_id)
                return {"status": "success", "data": result}
                
            elif tool_name == "terminate_cluster":
                from mcp_servers.databricks.api.clusters import clusters_client
                cluster_id = params.get("cluster_id") if params else None
                if not cluster_id:
                    return {"status": "error", "error": "cluster_id is required"}
                result = await clusters_client.terminate_cluster(cluster_id)
                return {"status": "success", "data": result}
                
            elif tool_name == "execute_sql":
                from mcp_servers.databricks.api.sql import sql_client
                statement = params.get("statement") if params else None
                if not statement:
                    return {"status": "error", "error": "statement is required"}

                warehouse_id = params.get("warehouse_id") if params else None
                catalog = params.get("catalog") if params else None
                schema = params.get("schema") if params else None

                try:
                    result = await sql_client.execute_statement(
                        statement=statement,
                        warehouse_id=warehouse_id,
                        catalog=catalog,
                        schema=schema
                    )
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(sql_client)
                
            elif tool_name == "list_warehouses":
                from mcp_servers.databricks.api.sql import sql_client
                try:
                    result = await sql_client.list_warehouses()
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(sql_client)

            elif tool_name == "get_warehouse":
                from mcp_servers.databricks.api.sql import sql_client
                try:
                    warehouse_id = params.get("warehouse_id")
                    if not warehouse_id:
                        return {"status": "error", "error": "warehouse_id is required"}
                    result = await sql_client.get_warehouse(warehouse_id)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(sql_client)

            elif tool_name == "start_warehouse":
                from mcp_servers.databricks.api.sql import sql_client
                try:
                    warehouse_id = params.get("warehouse_id")
                    if not warehouse_id:
                        return {"status": "error", "error": "warehouse_id is required"}
                    result = await sql_client.start_warehouse(warehouse_id)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(sql_client)

            elif tool_name == "stop_warehouse":
                from mcp_servers.databricks.api.sql import sql_client
                try:
                    warehouse_id = params.get("warehouse_id")
                    if not warehouse_id:
                        return {"status": "error", "error": "warehouse_id is required"}
                    result = await sql_client.stop_warehouse(warehouse_id)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(sql_client)

            elif tool_name == "list_jobs":
                from mcp_servers.databricks.api.jobs import jobs_client
                try:
                    result = await jobs_client.list_jobs()
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(jobs_client)
                
            elif tool_name == "get_job":
                from mcp_servers.databricks.api.jobs import jobs_client
                job_id = params.get("job_id") if params else None
                if not job_id:
                    return {"status": "error", "error": "job_id is required"}
                result = await jobs_client.get_job(job_id)
                return {"status": "success", "data": result}
                
            elif tool_name == "run_job":
                from mcp_servers.databricks.api.jobs import jobs_client
                job_id = params.get("job_id") if params else None
                if not job_id:
                    return {"status": "error", "error": "job_id is required"}
                result = await jobs_client.run_job(job_id)
                return {"status": "success", "data": result}

            # Notebook management tools
            elif tool_name == "list_notebooks":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                try:
                    path = params.get("path", "/") if params else "/"
                    object_type = params.get("object_type") if params else None
                    result = await notebooks_client.list_workspace_objects(path, object_type)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "get_notebook_info":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                path = params.get("path") if params else None
                if not path:
                    return {"status": "error", "error": "path is required"}
                try:
                    result = await notebooks_client.get_notebook_status(path)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "export_notebook":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                path = params.get("path") if params else None
                if not path:
                    return {"status": "error", "error": "path is required"}
                try:
                    format_type = params.get("format", "SOURCE") if params else "SOURCE"
                    direct_download = params.get("direct_download", False) if params else False
                    result = await notebooks_client.export_notebook(path, format_type, direct_download)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "create_notebook":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                path = params.get("path") if params else None
                if not path:
                    return {"status": "error", "error": "path is required"}
                try:
                    language = params.get("language", "PYTHON") if params else "PYTHON"
                    content = params.get("content") if params else None
                    result = await notebooks_client.create_notebook(path, language, content)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "import_notebook":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                path = params.get("path") if params else None
                content = params.get("content") if params else None
                if not path or not content:
                    return {"status": "error", "error": "path and content are required"}
                try:
                    format_type = params.get("format", "AUTO") if params else "AUTO"
                    language = params.get("language") if params else None
                    overwrite = params.get("overwrite", False) if params else False
                    result = await notebooks_client.import_notebook(path, content, format_type, language, overwrite)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "delete_notebook":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                path = params.get("path") if params else None
                if not path:
                    return {"status": "error", "error": "path is required"}
                try:
                    recursive = params.get("recursive", False) if params else False
                    result = await notebooks_client.delete_notebook(path, recursive)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "create_directory":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                path = params.get("path") if params else None
                if not path:
                    return {"status": "error", "error": "path is required"}
                try:
                    result = await notebooks_client.create_directory(path)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            elif tool_name == "search_notebooks":
                from mcp_servers.databricks.api.notebooks import NotebooksClient
                notebooks_client = NotebooksClient()
                query = params.get("query") if params else None
                if not query:
                    return {"status": "error", "error": "query is required"}
                try:
                    max_results = params.get("max_results", 25) if params else 25
                    path_prefix = params.get("path_prefix") if params else None
                    result = await notebooks_client.search_notebooks(query, max_results, path_prefix)
                    return {"status": "success", "data": result}
                finally:
                    await self._cleanup_sessions(notebooks_client)

            else:
                return {"status": "error", "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {str(e)}")
            return {"status": "error", "error": str(e)}


# Global MCP client instance
mcp_client = DatabricksMCPClient()


# MCP Tool Functions for the Data Scientist Agent
async def list_clusters() -> Dict[str, Any]:
    """List all Databricks clusters in the workspace."""
    result = await mcp_client._call_mcp_tool("list_clusters")
    return result


async def get_cluster(cluster_id: str) -> Dict[str, Any]:
    """Get information about a specific Databricks cluster."""
    result = await mcp_client._call_mcp_tool("get_cluster", {"cluster_id": cluster_id})
    return result


async def start_cluster(cluster_id: str) -> Dict[str, Any]:
    """Start a terminated Databricks cluster."""
    result = await mcp_client._call_mcp_tool("start_cluster", {"cluster_id": cluster_id})
    return result


async def terminate_cluster(cluster_id: str) -> Dict[str, Any]:
    """Terminate a running Databricks cluster."""
    result = await mcp_client._call_mcp_tool("terminate_cluster", {"cluster_id": cluster_id})
    return result


async def execute_sql(statement: str, warehouse_id: Optional[str] = None, 
                     catalog: Optional[str] = None, schema: Optional[str] = None) -> Dict[str, Any]:
    """Execute a SQL statement on Databricks."""
    params = {"statement": statement}
    if warehouse_id:
        params["warehouse_id"] = warehouse_id
    if catalog:
        params["catalog"] = catalog
    if schema:
        params["schema"] = schema
    
    result = await mcp_client._call_mcp_tool("execute_sql", params)
    return result


async def list_warehouses() -> Dict[str, Any]:
    """List all SQL warehouses in the workspace."""
    result = await mcp_client._call_mcp_tool("list_warehouses")
    return result


async def get_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Get information about a specific SQL warehouse."""
    result = await mcp_client._call_mcp_tool("get_warehouse", {"warehouse_id": warehouse_id})
    return result


async def start_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Start a stopped SQL warehouse."""
    result = await mcp_client._call_mcp_tool("start_warehouse", {"warehouse_id": warehouse_id})
    return result


async def stop_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Stop a running SQL warehouse."""
    result = await mcp_client._call_mcp_tool("stop_warehouse", {"warehouse_id": warehouse_id})
    return result


async def list_jobs() -> Dict[str, Any]:
    """List all jobs in the workspace."""
    result = await mcp_client._call_mcp_tool("list_jobs")
    return result


async def get_job(job_id: str) -> Dict[str, Any]:
    """Get information about a specific job."""
    result = await mcp_client._call_mcp_tool("get_job", {"job_id": job_id})
    return result


async def run_job(job_id: str) -> Dict[str, Any]:
    """Run a specific job."""
    result = await mcp_client._call_mcp_tool("run_job", {"job_id": job_id})
    return result


# Notebook Management Tools
async def list_notebooks(path: str = "/", object_type: Optional[str] = None) -> Dict[str, Any]:
    """List notebooks and directories in workspace.

    Args:
        path: Workspace path to list (default: root "/")
        object_type: Filter by object type (NOTEBOOK, DIRECTORY, FILE)

    Returns:
        Dictionary containing list of workspace objects
    """
    params = {"path": path}
    if object_type:
        params["object_type"] = object_type

    result = await mcp_client._call_mcp_tool("list_notebooks", params)
    return result


async def get_notebook_info(path: str) -> Dict[str, Any]:
    """Get metadata about a notebook or workspace object.

    Args:
        path: Full workspace path to the object

    Returns:
        Dictionary containing object metadata
    """
    result = await mcp_client._call_mcp_tool("get_notebook_info", {"path": path})
    return result


async def export_notebook(path: str, format: str = "SOURCE", direct_download: bool = False) -> Dict[str, Any]:
    """Export a notebook from the workspace.

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
    result = await mcp_client._call_mcp_tool("export_notebook", params)
    return result


async def create_notebook(path: str, language: str = "PYTHON", content: Optional[str] = None) -> Dict[str, Any]:
    """Create a new notebook in the workspace.

    Args:
        path: Target workspace path for the new notebook
        language: Programming language (PYTHON, SQL, SCALA, R)
        content: Initial notebook content (optional)

    Returns:
        Dictionary containing creation result
    """
    params = {
        "path": path,
        "language": language
    }
    if content:
        params["content"] = content

    result = await mcp_client._call_mcp_tool("create_notebook", params)
    return result


async def import_notebook(path: str, content: str, format: str = "AUTO",
                         language: Optional[str] = None, overwrite: bool = False) -> Dict[str, Any]:
    """Import a notebook to the workspace.

    Args:
        path: Target workspace path for the notebook
        content: Base64 encoded notebook content
        format: Import format (SOURCE, HTML, JUPYTER, DBC, AUTO)
        language: Programming language (PYTHON, SQL, SCALA, R)
        overwrite: Whether to overwrite existing notebook

    Returns:
        Dictionary containing import result
    """
    params = {
        "path": path,
        "content": content,
        "format": format,
        "overwrite": overwrite
    }
    if language:
        params["language"] = language

    result = await mcp_client._call_mcp_tool("import_notebook", params)
    return result


async def delete_notebook(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a notebook or directory from the workspace.

    Args:
        path: Full workspace path to delete
        recursive: Whether to delete directories recursively

    Returns:
        Dictionary containing deletion result
    """
    params = {
        "path": path,
        "recursive": recursive
    }
    result = await mcp_client._call_mcp_tool("delete_notebook", params)
    return result


async def create_directory(path: str) -> Dict[str, Any]:
    """Create a directory in the workspace.

    Args:
        path: Full workspace path for the new directory

    Returns:
        Dictionary containing creation result
    """
    result = await mcp_client._call_mcp_tool("create_directory", {"path": path})
    return result


async def search_notebooks(query: str, max_results: int = 25, path_prefix: Optional[str] = None) -> Dict[str, Any]:
    """Search for notebooks in the workspace.

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        path_prefix: Limit search to paths starting with this prefix

    Returns:
        List of matching notebook objects
    """
    params = {
        "query": query,
        "max_results": max_results
    }
    if path_prefix:
        params["path_prefix"] = path_prefix

    result = await mcp_client._call_mcp_tool("search_notebooks", params)
    return result


# Table Metadata Management Tools
async def get_table_metadata(table_name: str) -> Dict[str, Any]:
    """Get table metadata including MAGPIE context."""
    sql = f"""
    DESCRIBE TABLE EXTENDED {table_name}
    """
    result = await execute_ddl(sql)

    # Parse table properties to extract MAGPIE metadata
    metadata = {"table_name": table_name}

    if result.get("status") == "success":
        # Extract the actual data from the Databricks response
        data = result.get("data", {})
        rows = data.get("result", {}).get("data_array", [])

        logger.debug(f"Found {len(rows)} rows in DESCRIBE result")

        # Find the Table Properties row
        for row in rows:
            if isinstance(row, list) and len(row) >= 2:
                col_name = row[0] if len(row) > 0 else ""
                data_type = row[1] if len(row) > 1 else ""

                if col_name == "Table Properties":
                    props_str = data_type
                    logger.debug(f"Raw properties string: {props_str}")

                    # Extract MAGPIE properties from the properties string
                    if "magpie." in props_str:
                        metadata["has_magpie_context"] = True

                        # The properties are in format: [prop1=value1,prop2=value2,...]
                        # Remove the outer brackets first
                        if props_str.startswith('[') and props_str.endswith(']'):
                            props_str = props_str[1:-1]

                        # Split by commas, but be careful with nested JSON
                        # Use a more robust approach to extract each MAGPIE property

                        # Extract business context
                        if "magpie.business_context=" in props_str:
                            try:
                                start_idx = props_str.find("magpie.business_context=") + len("magpie.business_context=")
                                # Find the matching closing brace
                                brace_count = 0
                                end_idx = start_idx
                                for i, char in enumerate(props_str[start_idx:], start_idx):
                                    if char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            end_idx = i + 1
                                            break

                                if brace_count == 0:
                                    json_str = props_str[start_idx:end_idx]
                                    # Replace escaped quotes
                                    json_str = json_str.replace('\\"', '"')
                                    business_context = json.loads(json_str)
                                    metadata["business_context"] = business_context
                                    logger.debug(f"Parsed business context: {business_context}")
                            except Exception as e:
                                logger.warning(f"Could not parse business context: {e}")

                        # Extract field mappings
                        if "magpie.field_mappings=" in props_str:
                            try:
                                start_idx = props_str.find("magpie.field_mappings=") + len("magpie.field_mappings=")
                                # Find the matching closing brace
                                brace_count = 0
                                end_idx = start_idx
                                for i, char in enumerate(props_str[start_idx:], start_idx):
                                    if char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            end_idx = i + 1
                                            break

                                if brace_count == 0:
                                    json_str = props_str[start_idx:end_idx]
                                    # Replace escaped quotes
                                    json_str = json_str.replace('\\"', '"')
                                    field_mappings = json.loads(json_str)
                                    metadata["field_mappings"] = field_mappings
                                    logger.debug(f"Parsed field mappings: {field_mappings}")
                            except Exception as e:
                                logger.warning(f"Could not parse field mappings: {e}")

                        # Extract transformations
                        if "magpie.transformations=" in props_str:
                            try:
                                start_idx = props_str.find("magpie.transformations=") + len("magpie.transformations=")
                                # Find the matching closing brace
                                brace_count = 0
                                end_idx = start_idx
                                for i, char in enumerate(props_str[start_idx:], start_idx):
                                    if char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1
                                        if brace_count == 0:
                                            end_idx = i + 1
                                            break

                                if brace_count == 0:
                                    json_str = props_str[start_idx:end_idx]
                                    # Replace escaped quotes
                                    json_str = json_str.replace('\\"', '"')
                                    transformations = json.loads(json_str)
                                    metadata["transformations"] = transformations
                                    logger.debug(f"Parsed transformations: {transformations}")
                            except Exception as e:
                                logger.warning(f"Could not parse transformations: {e}")

                        # Extract common queries
                        if "magpie.common_queries=" in props_str:
                            try:
                                start_idx = props_str.find("magpie.common_queries=") + len("magpie.common_queries=")
                                # Find the matching closing bracket
                                bracket_count = 0
                                end_idx = start_idx
                                for i, char in enumerate(props_str[start_idx:], start_idx):
                                    if char == '[':
                                        bracket_count += 1
                                    elif char == ']':
                                        bracket_count -= 1
                                        if bracket_count == 0:
                                            end_idx = i + 1
                                            break

                                if bracket_count == 0:
                                    json_str = props_str[start_idx:end_idx]
                                    # Replace escaped quotes
                                    json_str = json_str.replace('\\"', '"')
                                    common_queries = json.loads(json_str)
                                    metadata["common_queries"] = common_queries
                                    logger.debug(f"Parsed common queries: {common_queries}")
                            except Exception as e:
                                logger.warning(f"Could not parse common queries: {e}")

                    break

    return {"status": "success", "data": metadata}


async def execute_ddl(statement: str) -> Dict[str, Any]:
    """Execute DDL statements (like ALTER TABLE) using available warehouse."""
    try:
        # Import the SQL client directly for DDL operations
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from mcp_servers.databricks.api.sql import sql_client

        try:
            # Get available warehouses and use the first one
            warehouses_result = await sql_client.list_warehouses()
            warehouse_id = None

            if warehouses_result and 'warehouses' in warehouses_result:
                warehouses = warehouses_result['warehouses']
                if warehouses:
                    warehouse_id = warehouses[0]['id']
                    logger.info(f"Using warehouse {warehouse_id} for DDL operation")

            if not warehouse_id:
                return {"status": "error", "error": "No warehouses available for DDL operations"}

            # Execute DDL with the available warehouse
            result = await sql_client.execute_statement(
                statement=statement,
                warehouse_id=warehouse_id,
                catalog=None,
                schema=None
            )
            return {"status": "success", "data": result}
        finally:
            await mcp_client._cleanup_sessions(sql_client)

    except Exception as e:
        logger.error(f"Error executing DDL: {str(e)}")
        return {"status": "error", "error": str(e)}


async def set_table_context(table_name: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Set table context metadata using Unity Catalog properties and column comments."""
    import json

    # Prepare JSON strings for table properties with error handling and sanitization
    try:
        # Sanitize data before JSON serialization
        sanitized_business_context = sanitize_for_json(context_data.get("business_context", {}))
        sanitized_field_mappings = sanitize_for_json(context_data.get("field_mappings", {}))
        sanitized_transformations = sanitize_for_json(context_data.get("transformations", {}))
        sanitized_common_queries = sanitize_for_json(context_data.get("common_queries", []))

        business_context = json.dumps(sanitized_business_context, ensure_ascii=False)
        field_mappings = json.dumps(sanitized_field_mappings, ensure_ascii=False)
        transformations = json.dumps(sanitized_transformations, ensure_ascii=False)
        common_queries = json.dumps(sanitized_common_queries, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.error(f"Error serializing context data to JSON: {e}")
        return {"status": "error", "error": f"Invalid context data format: {str(e)}"}

    # Log JSON sizes for debugging
    logger.debug(f"JSON sizes - business_context: {len(business_context)}, field_mappings: {len(field_mappings)}, transformations: {len(transformations)}")

    # Check if field_mappings is too large (Databricks has limits)
    if len(field_mappings) > 10000:  # Arbitrary limit to prevent issues
        logger.warning(f"Field mappings JSON is large ({len(field_mappings)} chars), may cause parsing issues")
        # Truncate field mappings if too large
        field_mappings_dict = context_data.get("field_mappings", {})
        truncated_mappings = {}
        for field, mapping in field_mappings_dict.items():
            truncated_mappings[field] = {
                "description": mapping.get("description", "")[:100] + "..." if len(mapping.get("description", "")) > 100 else mapping.get("description", "")
            }
        field_mappings = json.dumps(truncated_mappings)
        logger.info(f"Truncated field mappings to {len(field_mappings)} chars")

    # Safely escape strings for SQL with comprehensive sanitization
    def safe_sql_escape(text: str) -> str:
        """Safely escape text for SQL string literals."""
        if not text:
            return ""
        # Replace problematic characters
        text = text.replace("'", "''")  # Escape single quotes
        text = text.replace("\\", "\\\\")  # Escape backslashes
        text = text.replace("\n", "\\n")  # Escape newlines
        text = text.replace("\r", "\\r")  # Escape carriage returns
        text = text.replace("\t", "\\t")  # Escape tabs
        return text

    business_context = safe_sql_escape(business_context)
    field_mappings = safe_sql_escape(field_mappings)
    transformations = safe_sql_escape(transformations)
    common_queries = safe_sql_escape(common_queries)

    # Set table properties
    table_props_sql = f"""
    ALTER TABLE {table_name}
    SET TBLPROPERTIES (
        'magpie.business_context' = '{business_context}',
        'magpie.field_mappings' = '{field_mappings}',
        'magpie.transformations' = '{transformations}',
        'magpie.common_queries' = '{common_queries}',
        'magpie.last_updated' = '{datetime.now().isoformat()}',
        'magpie.version' = '1.0'
    )
    """

    result = await execute_ddl(table_props_sql)

    if result.get("status") != "success":
        return result

    # Also set column comments for field mappings so they appear in Databricks UI
    field_mappings_dict = context_data.get("field_mappings", {})
    transformations_dict = context_data.get("transformations", {})

    for field_name, field_info in field_mappings_dict.items():
        description = field_info.get("description", "")
        notes = field_info.get("notes", "")

        # Add transformation info if available
        if field_name in transformations_dict:
            transform_info = transformations_dict[field_name]
            transform_rule = transform_info.get("rule", "")
            if transform_rule:
                description += f" | Transform: {transform_rule}"

        # Combine description and notes
        comment = description
        if notes:
            comment += f" | {notes}"

        if comment:
            # Sanitize comment for SQL - escape quotes and remove problematic characters
            comment = comment.replace("'", "''")  # Escape single quotes
            comment = comment.replace('"', '""')  # Escape double quotes
            comment = comment.replace('\n', ' ')  # Replace newlines with spaces
            comment = comment.replace('\r', ' ')  # Replace carriage returns
            comment = comment.replace('\t', ' ')  # Replace tabs with spaces
            comment = comment.strip()  # Remove leading/trailing whitespace

            # Limit comment length to prevent issues
            if len(comment) > 500:
                comment = comment[:497] + "..."
                logger.warning(f"Truncated comment for column {field_name} to 500 characters")

            column_comment_sql = f"""
            ALTER TABLE {table_name}
            ALTER COLUMN {field_name} COMMENT '{comment}'
            """

            # Execute column comment (don't fail if this doesn't work)
            try:
                await execute_ddl(column_comment_sql)
                logger.info(f"Set comment for column {field_name}")
            except Exception as e:
                logger.warning(f"Could not set comment for column {field_name}: {e}")

    return result


async def load_context_from_csv(csv_path: str, table_name: str) -> Dict[str, Any]:
    """Load context from CSV file and apply to table."""
    try:
        import pandas as pd

        # Read CSV file
        df = pd.read_csv(csv_path)

        context = {
            "business_context": {},
            "field_mappings": {},
            "transformations": {},
            "common_queries": []
        }

        # Parse CSV data
        for _, row in df.iterrows():
            context_type = row['context_type']
            key = row['key']
            value = row['value']
            description = row.get('description', '')

            if context_type == 'business_context':
                context['business_context'][key] = value
            elif context_type == 'field_mapping':
                context['field_mappings'][key] = {
                    "description": value,
                    "notes": description
                }
            elif context_type == 'transformation':
                context['transformations'][key] = {
                    "rule": value,
                    "description": description
                }
            elif context_type == 'common_query':
                context['common_queries'].append({
                    "intent": key,
                    "template": value,
                    "description": description
                })

        # Apply context to table
        result = await set_table_context(table_name, context)

        if result.get("status") == "success":
            return {
                "status": "success",
                "message": f"Successfully loaded context from {csv_path} to {table_name}",
                "context": context
            }
        else:
            return {
                "status": "error",
                "error": f"Failed to apply context: {result.get('error')}"
            }

    except Exception as e:
        return {"status": "error", "error": str(e)}


# Synchronous wrapper functions for Google ADK compatibility
def list_clusters_sync() -> Dict[str, Any]:
    """Synchronous wrapper for list_clusters."""
    try:
        # Try to get existing event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, use thread executor
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, list_clusters())
                return future.result()
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            return asyncio.run(list_clusters())
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_cluster_sync(cluster_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_cluster."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_cluster(cluster_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(get_cluster(cluster_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def execute_sql_sync(statement: str, warehouse_id: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for execute_sql."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, execute_sql(statement, warehouse_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(execute_sql(statement, warehouse_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Synchronous wrappers for metadata tools
def get_table_metadata_sync(table_name: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_table_metadata."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_table_metadata(table_name))
                return future.result()
        except RuntimeError:
            return asyncio.run(get_table_metadata(table_name))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def set_table_context_sync(table_name: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for set_table_context with enhanced error handling."""
    try:
        # Import error handling utilities
        from .error_handlers import validate_table_context_data, create_user_friendly_error_message

        # Validate and sanitize context data
        sanitized_context = validate_table_context_data(context_data)

        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, set_table_context(table_name, sanitized_context))
                return future.result()
        except RuntimeError:
            return asyncio.run(set_table_context(table_name, sanitized_context))
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in set_table_context_sync: {e}")
        return {
            "status": "error",
            "error": "There was an issue with special characters in your descriptions. Please use simpler descriptions without quotes or special characters."
        }
    except Exception as e:
        logger.error(f"Error in set_table_context_sync: {e}")
        try:
            from .error_handlers import create_user_friendly_error_message
            error_msg = create_user_friendly_error_message(e)
        except:
            error_msg = str(e)
        return {"status": "error", "error": error_msg}


def read_csv_content_sync(csv_path: str) -> Dict[str, Any]:
    """Synchronous wrapper for reading CSV content."""
    try:
        return read_csv_content(csv_path)
    except Exception as e:
        return {"status": "error", "error": str(e)}


def parse_csv_content_only_sync(csv_content: str) -> Dict[str, Any]:
    """Synchronous wrapper for parsing CSV content only."""
    try:
        return parse_csv_content_only(csv_content)
    except Exception as e:
        return {"status": "error", "error": str(e)}


def convert_schema_csv_to_context_sync(csv_content: str) -> Dict[str, Any]:
    """Synchronous wrapper for converting schema CSV to context."""
    try:
        return convert_schema_csv_to_context(csv_content)
    except Exception as e:
        return {"status": "error", "error": str(e)}


def convert_schema_csv_to_context(csv_content: str) -> Dict[str, Any]:
    """
    Convert database schema CSV to table context format.

    Handles CSV files with database schema information (like AMOS exports)
    and converts them to our expected table context format.

    Args:
        csv_content: CSV content with schema information

    Returns:
        Converted context data or error
    """
    try:
        from io import StringIO
        csv_io = StringIO(csv_content)
        df = pd.read_csv(csv_io)

        # Check if this looks like a schema CSV (only require essential columns)
        essential_schema_columns = ['Name', 'Description']
        if not all(col in df.columns for col in essential_schema_columns):
            return {
                "status": "error",
                "error": f"CSV doesn't appear to be a schema file. Expected columns: {essential_schema_columns}, found: {list(df.columns)}"
            }

        # Convert to table context format
        context = {
            "business_context": {
                "description": "Aircraft utilization data from AMOS system",
                "source_system": "AMOS",
                "data_type": "Flight operations and aircraft utilization"
            },
            "field_mappings": {},
            "transformations": {},
            "common_queries": []
        }

        # Process each field (focus on Name and Description)
        for _, row in df.iterrows():
            field_name = str(row.get('Name', '')).strip()
            description = str(row.get('Description', '')).strip()
            keys = str(row.get('Keys', '')).strip() if 'Keys' in df.columns else ''
            field_type = str(row.get('Type', '')).strip() if 'Type' in df.columns else ''

            # Skip empty or header rows, and handle NaN values
            if not field_name or field_name in ['Name', '', 'nan']:
                continue

            # Clean up description (remove quotes and extra spaces)
            description = description.replace('""', '"').strip()

            # Create field mapping with essential information (keep descriptions shorter for JSON storage)
            field_mapping = {
                "description": description[:150] + "..." if len(description) > 150 else description
            }

            # Add optional information if available
            if keys:
                field_mapping["keys"] = keys
            if field_type:
                field_mapping["data_type"] = field_type
                field_mapping["notes"] = f"AMOS field type: {field_type}"

            context["field_mappings"][field_name] = field_mapping

            # Add common transformations for known field types (if Type column exists)
            if field_type and 'DATE_INT' in field_type:
                context["transformations"][field_name] = {
                    "rule": "Convert AMOS date integer to standard date format",
                    "description": "AMOS stores dates as integers, convert using appropriate date functions"
                }
            elif field_type and 'TIME' in field_type:
                context["transformations"][field_name] = {
                    "rule": "Convert minutes to hours:minutes format",
                    "description": "AMOS stores time as minutes since start of day"
                }

        return {
            "status": "success",
            "context": context,
            "fields_processed": len(context["field_mappings"]),
            "summary": {
                "business_context_items": len(context["business_context"]),
                "field_mappings": len(context["field_mappings"]),
                "transformations": len(context["transformations"]),
                "common_queries": len(context["common_queries"])
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Error converting schema CSV: {str(e)}"
        }


def process_csv_for_table_context_sync(csv_content: str, table_name: str) -> Dict[str, Any]:
    """Synchronous wrapper for processing CSV content."""
    try:
        # First try to parse as regular table context CSV
        parse_result = parse_csv_content_only(csv_content)

        # Check if regular parsing succeeded AND produced meaningful content
        if (parse_result.get("status") == "success" and
            parse_result.get("context", {}).get("field_mappings") and
            len(parse_result.get("context", {}).get("field_mappings", {})) > 0):

            # Regular table context CSV with actual content - proceed normally
            return process_csv_for_table_context(csv_content, table_name)

        else:
            # Either parsing failed OR it succeeded but produced empty content
            # Try to convert as schema CSV
            convert_result = convert_schema_csv_to_context(csv_content)

            if convert_result.get("status") == "success":
                # Successfully converted schema CSV - now apply it
                context = convert_result.get("context", {})
                result = set_table_context_sync(table_name, context)

                if result.get("status") == "success":
                    return {
                        "status": "success",
                        "message": f"Successfully converted and applied schema CSV to {table_name}",
                        "context_applied": context,
                        "fields_processed": convert_result.get("fields_processed"),
                        "summary": convert_result.get("summary"),
                        "conversion_note": "Converted from database schema format to table context format"
                    }
                else:
                    return {
                        "status": "error",
                        "error": f"Failed to apply converted context: {result.get('error')}"
                    }
            else:
                # Neither format worked
                parse_error = parse_result.get('error', 'No meaningful content found')
                convert_error = convert_result.get('error', 'Schema conversion failed')
                return {
                    "status": "error",
                    "error": f"CSV format not recognized. Tried table context format: {parse_error}. Tried schema format: {convert_error}"
                }

    except Exception as e:
        return {"status": "error", "error": str(e)}


def load_context_from_csv_sync(csv_path: str, table_name: str) -> Dict[str, Any]:
    """Synchronous wrapper for load_context_from_csv."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, load_context_from_csv(csv_path, table_name))
                return future.result()
        except RuntimeError:
            return asyncio.run(load_context_from_csv(csv_path, table_name))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def read_csv_content(csv_path: str) -> Dict[str, Any]:
    """
    Read and parse CSV file content for agent processing.
    This is a workaround for file upload limitations in web interfaces.

    Args:
        csv_path: Path to the CSV file

    Returns:
        Dictionary with parsed CSV content and formatted text
    """
    try:
        if not os.path.exists(csv_path):
            return {
                "status": "error",
                "error": f"CSV file not found: {csv_path}"
            }

        # Read the CSV file
        df = pd.read_csv(csv_path)

        # Convert to structured format
        csv_content = {
            "raw_data": df.to_dict('records'),
            "formatted_text": "",
            "summary": {
                "total_rows": len(df),
                "columns": list(df.columns),
                "file_path": csv_path
            }
        }

        # Create formatted text representation
        formatted_lines = [
            f"CSV File: {csv_path}",
            f"Total Rows: {len(df)}",
            f"Columns: {', '.join(df.columns)}",
            "",
            "Content:"
        ]

        # Add each row in a readable format
        for i, row in df.iterrows():
            formatted_lines.append(f"Row {i+1}:")
            for col in df.columns:
                value = row[col]
                formatted_lines.append(f"  {col}: {value}")
            formatted_lines.append("")

        csv_content["formatted_text"] = "\n".join(formatted_lines)

        # If this looks like a table context CSV, provide additional parsing
        if "context_type" in df.columns:
            csv_content["is_table_context"] = True
            csv_content["context_summary"] = _summarize_table_context(df)
        else:
            csv_content["is_table_context"] = False

        return {
            "status": "success",
            "data": csv_content
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Error reading CSV file: {str(e)}"
        }


def _summarize_table_context(df: pd.DataFrame) -> Dict[str, Any]:
    """Summarize table context CSV for easier agent understanding."""
    summary = {
        "business_context_items": 0,
        "field_mappings": 0,
        "transformations": 0,
        "common_queries": 0,
        "preview": []
    }

    # Count different types of context
    if "context_type" in df.columns:
        context_counts = df["context_type"].value_counts().to_dict()
        summary["business_context_items"] = context_counts.get("business_context", 0)
        summary["field_mappings"] = context_counts.get("field_mapping", 0)
        summary["transformations"] = context_counts.get("transformation", 0)
        summary["common_queries"] = context_counts.get("common_query", 0)

    # Create preview of content
    for i, row in df.head(5).iterrows():
        preview_item = {}
        for col in df.columns:
            preview_item[col] = str(row[col])[:100]  # Limit length
        summary["preview"].append(preview_item)

    return summary


def parse_csv_content_only(csv_content: str) -> Dict[str, Any]:
    """
    Parse CSV content (as text) without applying to any table.
    This is for validation and preview purposes.

    Args:
        csv_content: CSV content as a string

    Returns:
        Parsed context data
    """
    try:
        # Parse CSV content from string
        from io import StringIO
        csv_io = StringIO(csv_content)
        df = pd.read_csv(csv_io)

        # Parse the context data
        context = {
            "business_context": {},
            "field_mappings": {},
            "transformations": {},
            "common_queries": []
        }

        for _, row in df.iterrows():
            context_type = row.get("context_type", "")
            key = row.get("key", "")
            value = row.get("value", "")
            description = row.get("description", "")

            if context_type == "business_context":
                context["business_context"][key] = value
            elif context_type == "field_mapping":
                context["field_mappings"][key] = {
                    "description": value,
                    "notes": description
                }
            elif context_type == "transformation":
                context["transformations"][key] = {
                    "rule": value,
                    "description": description
                }
            elif context_type == "common_query":
                context["common_queries"].append({
                    "intent": key,
                    "template": value,
                    "description": description
                })

        return {
            "status": "success",
            "context": context,
            "rows_processed": len(df),
            "summary": {
                "business_context_items": len(context["business_context"]),
                "field_mappings": len(context["field_mappings"]),
                "transformations": len(context["transformations"]),
                "common_queries": len(context["common_queries"])
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Error parsing CSV content: {str(e)}"
        }


def process_csv_for_table_context(csv_content: str, table_name: str) -> Dict[str, Any]:
    """
    Process CSV content (as text) and apply it to a table.
    This is designed to work with CSV content passed as text from the agent.

    Args:
        csv_content: CSV content as a string
        table_name: Target table name

    Returns:
        Result of applying the context
    """
    try:
        # First parse the CSV content
        parse_result = parse_csv_content_only(csv_content)

        if parse_result.get("status") != "success":
            return parse_result

        context = parse_result.get("context", {})

        # Apply the context to the table
        result = set_table_context_sync(table_name, context)

        if result.get("status") == "success":
            return {
                "status": "success",
                "message": f"Successfully applied CSV context to {table_name}",
                "context_applied": context,
                "rows_processed": parse_result.get("rows_processed"),
                "summary": parse_result.get("summary")
            }
        else:
            return {
                "status": "error",
                "error": f"Failed to apply context: {result.get('error')}"
            }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Error processing CSV content: {str(e)}"
        }


def start_cluster_sync(cluster_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for start_cluster."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, start_cluster(cluster_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(start_cluster(cluster_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def terminate_cluster_sync(cluster_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for terminate_cluster."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, terminate_cluster(cluster_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(terminate_cluster(cluster_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def list_warehouses_sync() -> Dict[str, Any]:
    """Synchronous wrapper for list_warehouses."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, list_warehouses())
                return future.result()
        except RuntimeError:
            return asyncio.run(list_warehouses())
    except Exception as e:
        return {"status": "error", "error": str(e)}


def list_jobs_sync() -> Dict[str, Any]:
    """Synchronous wrapper for list_jobs."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, list_jobs())
                return future.result()
        except RuntimeError:
            return asyncio.run(list_jobs())
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_job_sync(job_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_job."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_job(job_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(get_job(job_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_job_sync(job_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for run_job."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, run_job(job_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(run_job(job_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_warehouse_sync(warehouse_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_warehouse."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_warehouse(warehouse_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(get_warehouse(warehouse_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def start_warehouse_sync(warehouse_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for start_warehouse."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, start_warehouse(warehouse_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(start_warehouse(warehouse_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def stop_warehouse_sync(warehouse_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for stop_warehouse."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, stop_warehouse(warehouse_id))
                return future.result()
        except RuntimeError:
            return asyncio.run(stop_warehouse(warehouse_id))
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Synchronous wrappers for notebook management tools
def list_notebooks_sync(path: str = "/", object_type: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for list_notebooks."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, list_notebooks(path, object_type))
                return future.result()
        except RuntimeError:
            return asyncio.run(list_notebooks(path, object_type))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_notebook_info_sync(path: str) -> Dict[str, Any]:
    """Synchronous wrapper for get_notebook_info."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_notebook_info(path))
                return future.result()
        except RuntimeError:
            return asyncio.run(get_notebook_info(path))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def export_notebook_sync(path: str, format: str = "SOURCE", direct_download: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for export_notebook."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, export_notebook(path, format, direct_download))
                return future.result()
        except RuntimeError:
            return asyncio.run(export_notebook(path, format, direct_download))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def create_notebook_sync(path: str, language: str = "PYTHON", content: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for create_notebook."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, create_notebook(path, language, content))
                return future.result()
        except RuntimeError:
            return asyncio.run(create_notebook(path, language, content))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def import_notebook_sync(path: str, content: str, format: str = "AUTO",
                        language: Optional[str] = None, overwrite: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for import_notebook."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, import_notebook(path, content, format, language, overwrite))
                return future.result()
        except RuntimeError:
            return asyncio.run(import_notebook(path, content, format, language, overwrite))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def delete_notebook_sync(path: str, recursive: bool = False) -> Dict[str, Any]:
    """Synchronous wrapper for delete_notebook."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, delete_notebook(path, recursive))
                return future.result()
        except RuntimeError:
            return asyncio.run(delete_notebook(path, recursive))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def create_directory_sync(path: str) -> Dict[str, Any]:
    """Synchronous wrapper for create_directory."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, create_directory(path))
                return future.result()
        except RuntimeError:
            return asyncio.run(create_directory(path))
    except Exception as e:
        return {"status": "error", "error": str(e)}


def search_notebooks_sync(query: str, max_results: int = 25, path_prefix: Optional[str] = None) -> Dict[str, Any]:
    """Synchronous wrapper for search_notebooks."""
    try:
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, search_notebooks(query, max_results, path_prefix))
                return future.result()
        except RuntimeError:
            return asyncio.run(search_notebooks(query, max_results, path_prefix))
    except Exception as e:
        return {"status": "error", "error": str(e)}
