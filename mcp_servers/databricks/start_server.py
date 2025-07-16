#!/usr/bin/env python3
"""
Startup script for the MAGPIE Databricks MCP Server.

This script provides a convenient way to start the Databricks MCP server
with proper environment setup and error handling.
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler("databricks_mcp_server.log")
        ]
    )

def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = [
        "DATABRICKS_WORKSPACE_URL",
        "DATABRICKS_CLIENT_ID", 
        "DATABRICKS_CLIENT_SECRET",
        "DATABRICKS_TENANT_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}", file=sys.stderr)
        print("Please set these variables before starting the server.", file=sys.stderr)
        return False
    
    return True

def main():
    """Main entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting MAGPIE Databricks MCP Server")
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    try:
        # Import and run the server
        from server import main as server_main
        server_main()
    except ImportError as e:
        logger.error(f"Failed to import server module: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
