"""
Databricks SQL API client.

Provides functionality for executing SQL statements and managing
SQL warehouses in Databricks.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from mcp_servers.databricks.api.base import BaseDatabricksClient
from mcp_servers.databricks.config import settings

logger = logging.getLogger(__name__)


class SQLClient(BaseDatabricksClient):
    """Client for Databricks SQL API operations."""
    
    async def execute_statement(
        self,
        statement: str,
        warehouse_id: Optional[str] = None,
        catalog: Optional[str] = None,
        schema: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a SQL statement.
        
        Args:
            statement: SQL statement to execute
            warehouse_id: SQL warehouse ID (uses default if not provided)
            catalog: Catalog to use for the statement
            schema: Schema to use for the statement
            parameters: Parameters for parameterized queries
            
        Returns:
            Dictionary containing query results
        """
        # Use provided warehouse_id or fall back to configured default
        if not warehouse_id:
            warehouse_id = settings.DATABRICKS_WAREHOUSE_ID
            if not warehouse_id:
                raise ValueError("warehouse_id is required (not provided and DATABRICKS_WAREHOUSE_ID not set)")
        
        logger.info(f"Executing SQL statement on warehouse {warehouse_id}")
        
        # Prepare the request payload
        payload = {
            "warehouse_id": warehouse_id,
            "statement": statement,
            "wait_timeout": "30s"  # Wait up to 30 seconds for completion
        }
        
        # Add optional parameters
        if catalog:
            payload["catalog"] = catalog
        if schema:
            payload["schema"] = schema
        if parameters:
            payload["parameters"] = parameters
        
        # Execute the statement
        response = await self.post("/api/2.0/sql/statements", data=payload)
        
        # If the statement is still running, wait for completion
        statement_id = response.get("statement_id")
        if statement_id and response.get("status", {}).get("state") == "RUNNING":
            logger.info(f"Statement {statement_id} is running, waiting for completion...")
            response = await self._wait_for_statement_completion(statement_id)
        
        return response
    
    async def _wait_for_statement_completion(
        self,
        statement_id: str,
        max_wait_time: int = 300  # 5 minutes
    ) -> Dict[str, Any]:
        """
        Wait for a SQL statement to complete.
        
        Args:
            statement_id: ID of the statement to wait for
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Final statement result
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if we've exceeded the maximum wait time
            if asyncio.get_event_loop().time() - start_time > max_wait_time:
                logger.warning(f"Statement {statement_id} timed out after {max_wait_time} seconds")
                break
            
            # Get the current status
            response = await self.get(f"/api/2.0/sql/statements/{statement_id}")
            state = response.get("status", {}).get("state")
            
            if state in ["SUCCEEDED", "FAILED", "CANCELED"]:
                logger.info(f"Statement {statement_id} completed with state: {state}")
                return response
            
            # Wait before checking again
            await asyncio.sleep(2)
        
        # Return the last known status if we timed out
        return await self.get(f"/api/2.0/sql/statements/{statement_id}")
    
    async def get_statement_result(self, statement_id: str) -> Dict[str, Any]:
        """
        Get the result of a SQL statement.
        
        Args:
            statement_id: ID of the statement
            
        Returns:
            Dictionary containing statement results
        """
        logger.info(f"Getting result for statement {statement_id}")
        return await self.get(f"/api/2.0/sql/statements/{statement_id}")
    
    async def cancel_statement(self, statement_id: str) -> Dict[str, Any]:
        """
        Cancel a running SQL statement.
        
        Args:
            statement_id: ID of the statement to cancel
            
        Returns:
            Dictionary containing cancellation result
        """
        logger.info(f"Cancelling statement {statement_id}")
        return await self.post(f"/api/2.0/sql/statements/{statement_id}/cancel")
    
    async def list_warehouses(self) -> Dict[str, Any]:
        """
        List all SQL warehouses.
        
        Returns:
            Dictionary containing warehouse information
        """
        logger.info("Listing SQL warehouses")
        return await self.get("/api/2.0/sql/warehouses")
    
    async def get_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Get information about a specific SQL warehouse.

        Args:
            warehouse_id: ID of the warehouse

        Returns:
            Dictionary containing warehouse details
        """
        logger.info(f"Getting warehouse info for {warehouse_id}")
        return await self.get(f"/api/2.0/sql/warehouses/{warehouse_id}")

    async def start_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Start a SQL warehouse.

        Args:
            warehouse_id: ID of the warehouse to start

        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Starting warehouse {warehouse_id}")
        return await self.post(f"/api/2.0/sql/warehouses/{warehouse_id}/start")

    async def stop_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Stop a SQL warehouse.

        Args:
            warehouse_id: ID of the warehouse to stop

        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Stopping warehouse {warehouse_id}")
        return await self.post(f"/api/2.0/sql/warehouses/{warehouse_id}/stop")

    async def create_warehouse(self, warehouse_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new SQL warehouse.

        Args:
            warehouse_config: Warehouse configuration dictionary

        Returns:
            Dictionary containing the new warehouse information
        """
        logger.info(f"Creating warehouse with config: {warehouse_config}")

        # Validate required fields
        required_fields = ["name", "cluster_size"]
        for field in required_fields:
            if field not in warehouse_config:
                raise ValueError(f"Missing required field: {field}")

        return await self.post("/api/2.0/sql/warehouses", data=warehouse_config)

    async def delete_warehouse(self, warehouse_id: str) -> Dict[str, Any]:
        """
        Delete a SQL warehouse.

        Args:
            warehouse_id: ID of the warehouse to delete

        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Deleting warehouse {warehouse_id}")
        return await self.delete(f"/api/2.0/sql/warehouses/{warehouse_id}")

    async def edit_warehouse(self, warehouse_id: str, warehouse_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit/update a SQL warehouse configuration.

        Args:
            warehouse_id: ID of the warehouse to edit
            warehouse_config: Updated warehouse configuration

        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Editing warehouse {warehouse_id} with config: {warehouse_config}")
        return await self.post(f"/api/2.0/sql/warehouses/{warehouse_id}/edit", data=warehouse_config)


# Global client instance
sql_client = SQLClient()


# Convenience functions for backward compatibility
async def execute_statement(
    statement: str,
    warehouse_id: Optional[str] = None,
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a SQL statement."""
    return await sql_client.execute_statement(
        statement=statement,
        warehouse_id=warehouse_id,
        catalog=catalog,
        schema=schema,
        parameters=parameters
    )


async def get_statement_result(statement_id: str) -> Dict[str, Any]:
    """Get statement result."""
    return await sql_client.get_statement_result(statement_id)


async def cancel_statement(statement_id: str) -> Dict[str, Any]:
    """Cancel a statement."""
    return await sql_client.cancel_statement(statement_id)


async def list_warehouses() -> Dict[str, Any]:
    """List SQL warehouses."""
    return await sql_client.list_warehouses()


async def get_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Get warehouse information."""
    return await sql_client.get_warehouse(warehouse_id)


async def start_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Start a SQL warehouse."""
    return await sql_client.start_warehouse(warehouse_id)


async def stop_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Stop a SQL warehouse."""
    return await sql_client.stop_warehouse(warehouse_id)


async def create_warehouse(warehouse_config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new SQL warehouse."""
    return await sql_client.create_warehouse(warehouse_config)


async def delete_warehouse(warehouse_id: str) -> Dict[str, Any]:
    """Delete a SQL warehouse."""
    return await sql_client.delete_warehouse(warehouse_id)


async def edit_warehouse(warehouse_id: str, warehouse_config: Dict[str, Any]) -> Dict[str, Any]:
    """Edit a SQL warehouse."""
    return await sql_client.edit_warehouse(warehouse_id, warehouse_config)
