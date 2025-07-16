"""
Centralized Databricks MCP Server for MAGPIE Platform.

This module implements a standalone MCP server that provides tools for interacting 
with Databricks APIs using Azure service principal authentication. It follows the 
Model Context Protocol standard and can be consumed by multiple agents across 
the MAGPIE platform.
"""

import asyncio
import json
import logging
import sys
import os
from typing import Any, Dict, List, Optional
from mcp.server import FastMCP
from mcp.types import TextContent
from mcp.server.stdio import stdio_server

# Import API clients
from .api.clusters import clusters_client
from .api.sql import sql_client
from .api.jobs import jobs_client
from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    filename="databricks_mcp.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _unwrap_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unwrap parameters from MCP client structure.
    
    MCP clients may pass parameters in nested structure like:
    {"params": {"actual_parameter": "value"}}
    
    This function handles both nested and flat parameter structures.
    
    Args:
        params: Parameters from MCP client
        
    Returns:
        Unwrapped parameters dictionary
    """
    if 'params' in params and isinstance(params['params'], dict):
        return params['params']
    return params


class DatabricksMCPServer(FastMCP):
    """
    Centralized MCP server for Databricks APIs with service principal authentication.
    
    This server provides a comprehensive set of tools for interacting with Databricks
    and can be consumed by multiple agents across the MAGPIE platform.
    """
    
    def __init__(self):
        """Initialize the Databricks MCP server."""
        super().__init__(
            name="magpie-databricks-mcp",
            version="1.0.0",
            instructions="Centralized Databricks MCP server for MAGPIE platform with service principal authentication"
        )
        
        logger.info("Initializing MAGPIE Databricks MCP server")
        logger.info(f"Databricks workspace: {settings.DATABRICKS_WORKSPACE_URL}")
        logger.info(f"Using service principal authentication")
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all Databricks MCP tools."""
        
        # Cluster management tools
        @self.tool(
            name="list_clusters",
            description="List all Databricks clusters in the workspace",
        )
        async def list_clusters(params: Dict[str, Any]) -> List[TextContent]:
            logger.info("Listing clusters")
            try:
                result = await clusters_client.list_clusters()
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error listing clusters: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]
        
        @self.tool(
            name="get_cluster",
            description="Get information about a specific Databricks cluster. Parameters: cluster_id (required)",
        )
        async def get_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting cluster info with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                cluster_id = actual_params.get("cluster_id")
                if not cluster_id:
                    raise ValueError("cluster_id is required")
                
                result = await clusters_client.get_cluster(cluster_id)
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error getting cluster info: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]
        
        @self.tool(
            name="create_cluster",
            description="Create a new Databricks cluster. Parameters: cluster_name (required), spark_version (required), node_type_id (required), num_workers (optional), autotermination_minutes (optional)",
        )
        async def create_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Creating cluster with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                result = await clusters_client.create_cluster(actual_params)
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error creating cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]
        
        @self.tool(
            name="start_cluster",
            description="Start a terminated Databricks cluster. Parameters: cluster_id (required)",
        )
        async def start_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Starting cluster with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                cluster_id = actual_params.get("cluster_id")
                if not cluster_id:
                    raise ValueError("cluster_id is required")
                
                result = await clusters_client.start_cluster(cluster_id)
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error starting cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]
        
        @self.tool(
            name="terminate_cluster",
            description="Terminate a Databricks cluster. Parameters: cluster_id (required)",
        )
        async def terminate_cluster(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Terminating cluster with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                cluster_id = actual_params.get("cluster_id")
                if not cluster_id:
                    raise ValueError("cluster_id is required")
                
                result = await clusters_client.terminate_cluster(cluster_id)
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error terminating cluster: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]
        
        # SQL execution tools
        @self.tool(
            name="execute_sql",
            description="Execute a SQL statement on Databricks. Parameters: statement (required), warehouse_id (optional - uses default if not provided), catalog (optional), schema (optional)",
        )
        async def execute_sql(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Executing SQL with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                statement = actual_params.get("statement")
                if not statement:
                    raise ValueError("statement is required")
                
                warehouse_id = actual_params.get("warehouse_id")
                catalog = actual_params.get("catalog")
                schema = actual_params.get("schema")
                
                result = await sql_client.execute_statement(
                    statement=statement,
                    warehouse_id=warehouse_id,
                    catalog=catalog,
                    schema=schema
                )
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error executing SQL: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]
        
        @self.tool(
            name="list_warehouses",
            description="List all SQL warehouses in the workspace",
        )
        async def list_warehouses(params: Dict[str, Any]) -> List[TextContent]:
            logger.info("Listing SQL warehouses")
            try:
                result = await sql_client.list_warehouses()
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error listing warehouses: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]

        # Job management tools
        @self.tool(
            name="list_jobs",
            description="List all Databricks jobs in the workspace. Parameters: limit (optional, default 25), offset (optional, default 0)",
        )
        async def list_jobs(params: Dict[str, Any]) -> List[TextContent]:
            logger.info("Listing jobs")
            try:
                actual_params = _unwrap_params(params)
                limit = actual_params.get("limit", 25)
                offset = actual_params.get("offset", 0)

                result = await jobs_client.list_jobs(limit=limit, offset=offset)
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error listing jobs: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]

        @self.tool(
            name="get_job",
            description="Get information about a specific Databricks job. Parameters: job_id (required)",
        )
        async def get_job(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Getting job info with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                job_id = actual_params.get("job_id")
                if not job_id:
                    raise ValueError("job_id is required")

                result = await jobs_client.get_job(int(job_id))
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error getting job info: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]

        @self.tool(
            name="run_job",
            description="Run a Databricks job immediately. Parameters: job_id (required), notebook_params (optional)",
        )
        async def run_job(params: Dict[str, Any]) -> List[TextContent]:
            logger.info(f"Running job with params: {params}")
            try:
                actual_params = _unwrap_params(params)
                job_id = actual_params.get("job_id")
                if not job_id:
                    raise ValueError("job_id is required")

                notebook_params = actual_params.get("notebook_params")
                result = await jobs_client.run_job(int(job_id), notebook_params)
                return [{"text": json.dumps(result, indent=2)}]
            except Exception as e:
                logger.error(f"Error running job: {str(e)}")
                return [{"text": json.dumps({"error": str(e)}, indent=2)}]


def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting MAGPIE Databricks MCP server")
        
        # Turn off buffering in stdout
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(line_buffering=True)
        
        server = DatabricksMCPServer()
        
        # Use the FastMCP run method which handles async internally
        server.run()
        
    except Exception as e:
        logger.error(f"Error in MAGPIE Databricks MCP server: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
