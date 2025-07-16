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
from typing import Dict, Any, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
