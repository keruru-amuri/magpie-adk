"""
Databricks Clusters API client.

Provides functionality for managing Databricks clusters including
listing, creating, starting, stopping, and terminating clusters.
"""

import logging
from typing import Any, Dict, List, Optional
from .base import BaseDatabricksClient

logger = logging.getLogger(__name__)


class ClustersClient(BaseDatabricksClient):
    """Client for Databricks Clusters API operations."""
    
    async def list_clusters(self) -> Dict[str, Any]:
        """
        List all clusters in the workspace.
        
        Returns:
            Dictionary containing cluster information
        """
        logger.info("Listing all clusters")
        return await self.get("/api/2.0/clusters/list")
    
    async def get_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Get information about a specific cluster.
        
        Args:
            cluster_id: The ID of the cluster
            
        Returns:
            Dictionary containing cluster details
        """
        logger.info(f"Getting cluster info for {cluster_id}")
        return await self.get("/api/2.0/clusters/get", params={"cluster_id": cluster_id})
    
    async def create_cluster(self, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new cluster.
        
        Args:
            cluster_config: Cluster configuration dictionary
            
        Returns:
            Dictionary containing the new cluster ID
        """
        logger.info(f"Creating cluster with config: {cluster_config}")
        
        # Validate required fields
        required_fields = ["cluster_name", "spark_version", "node_type_id"]
        for field in required_fields:
            if field not in cluster_config:
                raise ValueError(f"Missing required field: {field}")
        
        return await self.post("/api/2.0/clusters/create", data=cluster_config)
    
    async def start_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Start a terminated cluster.
        
        Args:
            cluster_id: The ID of the cluster to start
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Starting cluster {cluster_id}")
        return await self.post("/api/2.0/clusters/start", data={"cluster_id": cluster_id})
    
    async def restart_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Restart a cluster.
        
        Args:
            cluster_id: The ID of the cluster to restart
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Restarting cluster {cluster_id}")
        return await self.post("/api/2.0/clusters/restart", data={"cluster_id": cluster_id})
    
    async def terminate_cluster(self, cluster_id: str) -> Dict[str, Any]:
        """
        Terminate a cluster.
        
        Args:
            cluster_id: The ID of the cluster to terminate
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Terminating cluster {cluster_id}")
        return await self.post("/api/2.0/clusters/delete", data={"cluster_id": cluster_id})
    
    async def resize_cluster(self, cluster_id: str, num_workers: int) -> Dict[str, Any]:
        """
        Resize a cluster by changing the number of workers.
        
        Args:
            cluster_id: The ID of the cluster to resize
            num_workers: New number of worker nodes
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Resizing cluster {cluster_id} to {num_workers} workers")
        return await self.post("/api/2.0/clusters/resize", data={
            "cluster_id": cluster_id,
            "num_workers": num_workers
        })


# Global client instance
clusters_client = ClustersClient()


# Convenience functions for backward compatibility
async def list_clusters() -> Dict[str, Any]:
    """List all clusters."""
    return await clusters_client.list_clusters()


async def get_cluster(cluster_id: str) -> Dict[str, Any]:
    """Get cluster information."""
    return await clusters_client.get_cluster(cluster_id)


async def create_cluster(cluster_config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new cluster."""
    return await clusters_client.create_cluster(cluster_config)


async def start_cluster(cluster_id: str) -> Dict[str, Any]:
    """Start a cluster."""
    return await clusters_client.start_cluster(cluster_id)


async def restart_cluster(cluster_id: str) -> Dict[str, Any]:
    """Restart a cluster."""
    return await clusters_client.restart_cluster(cluster_id)


async def terminate_cluster(cluster_id: str) -> Dict[str, Any]:
    """Terminate a cluster."""
    return await clusters_client.terminate_cluster(cluster_id)


async def resize_cluster(cluster_id: str, num_workers: int) -> Dict[str, Any]:
    """Resize a cluster."""
    return await clusters_client.resize_cluster(cluster_id, num_workers)
