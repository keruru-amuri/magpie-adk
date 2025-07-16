"""
Databricks Jobs API client.

Provides functionality for managing Databricks jobs including
creating, running, monitoring, and managing job executions.
"""

import logging
import asyncio
from typing import Any, Dict, List, Optional
from mcp_servers.databricks.api.base import BaseDatabricksClient

logger = logging.getLogger(__name__)


class JobsClient(BaseDatabricksClient):
    """Client for Databricks Jobs API operations."""
    
    async def list_jobs(self, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
        """
        List jobs in the workspace.
        
        Args:
            limit: Maximum number of jobs to return
            offset: Offset for pagination
            
        Returns:
            Dictionary containing job information
        """
        logger.info(f"Listing jobs (limit: {limit}, offset: {offset})")
        params = {"limit": limit, "offset": offset}
        return await self.get("/api/2.1/jobs/list", params=params)
    
    async def get_job(self, job_id: int) -> Dict[str, Any]:
        """
        Get information about a specific job.
        
        Args:
            job_id: The ID of the job
            
        Returns:
            Dictionary containing job details
        """
        logger.info(f"Getting job info for {job_id}")
        return await self.get("/api/2.1/jobs/get", params={"job_id": job_id})
    
    async def create_job(self, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job.
        
        Args:
            job_config: Job configuration dictionary
            
        Returns:
            Dictionary containing the new job ID
        """
        logger.info(f"Creating job with config: {job_config}")
        
        # Validate required fields
        if "name" not in job_config:
            raise ValueError("Job name is required")
        if "tasks" not in job_config:
            raise ValueError("Job tasks are required")
        
        return await self.post("/api/2.1/jobs/create", data=job_config)
    
    async def update_job(self, job_id: int, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing job.
        
        Args:
            job_id: The ID of the job to update
            job_config: Updated job configuration
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Updating job {job_id}")
        data = {"job_id": job_id, **job_config}
        return await self.post("/api/2.1/jobs/update", data=data)
    
    async def delete_job(self, job_id: int) -> Dict[str, Any]:
        """
        Delete a job.
        
        Args:
            job_id: The ID of the job to delete
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Deleting job {job_id}")
        return await self.post("/api/2.1/jobs/delete", data={"job_id": job_id})
    
    async def run_job(self, job_id: int, notebook_params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Run a job immediately.
        
        Args:
            job_id: The ID of the job to run
            notebook_params: Parameters to pass to notebook tasks
            
        Returns:
            Dictionary containing the run ID
        """
        logger.info(f"Running job {job_id}")
        data = {"job_id": job_id}
        if notebook_params:
            data["notebook_params"] = notebook_params
        
        return await self.post("/api/2.1/jobs/run-now", data=data)
    
    async def get_run(self, run_id: int) -> Dict[str, Any]:
        """
        Get information about a job run.
        
        Args:
            run_id: The ID of the run
            
        Returns:
            Dictionary containing run details
        """
        logger.info(f"Getting run info for {run_id}")
        return await self.get("/api/2.1/jobs/runs/get", params={"run_id": run_id})
    
    async def list_runs(self, job_id: Optional[int] = None, limit: int = 25) -> Dict[str, Any]:
        """
        List job runs.
        
        Args:
            job_id: Filter runs for a specific job (optional)
            limit: Maximum number of runs to return
            
        Returns:
            Dictionary containing run information
        """
        logger.info(f"Listing runs for job {job_id if job_id else 'all jobs'}")
        params = {"limit": limit}
        if job_id:
            params["job_id"] = job_id
        
        return await self.get("/api/2.1/jobs/runs/list", params=params)
    
    async def cancel_run(self, run_id: int) -> Dict[str, Any]:
        """
        Cancel a job run.
        
        Args:
            run_id: The ID of the run to cancel
            
        Returns:
            Dictionary containing operation result
        """
        logger.info(f"Cancelling run {run_id}")
        return await self.post("/api/2.1/jobs/runs/cancel", data={"run_id": run_id})
    
    async def wait_for_run_completion(
        self,
        run_id: int,
        max_wait_time: int = 3600  # 1 hour
    ) -> Dict[str, Any]:
        """
        Wait for a job run to complete.
        
        Args:
            run_id: The ID of the run to wait for
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Final run result
        """
        logger.info(f"Waiting for run {run_id} to complete")
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if we've exceeded the maximum wait time
            if asyncio.get_event_loop().time() - start_time > max_wait_time:
                logger.warning(f"Run {run_id} timed out after {max_wait_time} seconds")
                break
            
            # Get the current status
            response = await self.get_run(run_id)
            state = response.get("state", {}).get("life_cycle_state")
            
            if state in ["TERMINATED", "SKIPPED", "INTERNAL_ERROR"]:
                result_state = response.get("state", {}).get("result_state")
                logger.info(f"Run {run_id} completed with state: {state}, result: {result_state}")
                return response
            
            # Wait before checking again
            await asyncio.sleep(10)
        
        # Return the last known status if we timed out
        return await self.get_run(run_id)


# Global client instance
jobs_client = JobsClient()


# Convenience functions for backward compatibility
async def list_jobs(limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    """List jobs."""
    return await jobs_client.list_jobs(limit, offset)


async def get_job(job_id: int) -> Dict[str, Any]:
    """Get job information."""
    return await jobs_client.get_job(job_id)


async def create_job(job_config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new job."""
    return await jobs_client.create_job(job_config)


async def run_job(job_id: int, notebook_params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Run a job."""
    return await jobs_client.run_job(job_id, notebook_params)


async def get_run(run_id: int) -> Dict[str, Any]:
    """Get run information."""
    return await jobs_client.get_run(run_id)


async def cancel_run(run_id: int) -> Dict[str, Any]:
    """Cancel a run."""
    return await jobs_client.cancel_run(run_id)
