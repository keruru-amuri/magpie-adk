#!/usr/bin/env python3
"""
Test script for the MAGPIE Databricks MCP Server.

This script tests the basic functionality of the Databricks MCP server
including configuration validation and basic API connectivity.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

async def test_configuration():
    """Test configuration loading and validation."""
    print("Testing configuration...")

    try:
        from mcp_servers.databricks.config import settings
        print(f"✓ Configuration loaded successfully")
        print(f"  - Workspace URL: {settings.DATABRICKS_WORKSPACE_URL}")
        print(f"  - Client ID: {settings.DATABRICKS_CLIENT_ID[:8]}...")
        print(f"  - Tenant ID: {settings.DATABRICKS_TENANT_ID}")
        return True
    except Exception as e:
        print(f"✗ Configuration failed: {e}")
        return False

async def test_authentication():
    """Test Azure AD authentication."""
    print("\nTesting authentication...")

    try:
        from mcp_servers.databricks.auth import auth
        token = await auth.get_access_token()
        print(f"✓ Authentication successful")
        print(f"  - Token acquired: {token[:20]}...")
        return True
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False

async def test_api_clients():
    """Test API client initialization."""
    print("\nTesting API clients...")

    try:
        from mcp_servers.databricks.api.clusters import clusters_client
        from mcp_servers.databricks.api.sql import sql_client
        from mcp_servers.databricks.api.jobs import jobs_client

        print("✓ API clients initialized successfully")
        print("  - Clusters client: Ready")
        print("  - SQL client: Ready")
        print("  - Jobs client: Ready")
        return True
    except Exception as e:
        print(f"✗ API client initialization failed: {e}")
        return False

async def test_basic_api_call():
    """Test a basic API call (list clusters)."""
    print("\nTesting basic API call...")

    try:
        from mcp_servers.databricks.api.clusters import clusters_client
        result = await clusters_client.list_clusters()
        print("✓ Basic API call successful")
        print(f"  - Response received: {type(result)}")
        return True
    except Exception as e:
        print(f"✗ Basic API call failed: {e}")
        print("  This is expected if Databricks credentials are not properly configured")
        return False

async def test_server_initialization():
    """Test MCP server initialization."""
    print("\nTesting MCP server initialization...")

    try:
        from mcp_servers.databricks.server import DatabricksMCPServer
        server = DatabricksMCPServer()
        print("✓ MCP server initialized successfully")
        print(f"  - Server name: {server.name}")
        print(f"  - Server type: {type(server).__name__}")
        return True
    except Exception as e:
        print(f"✗ MCP server initialization failed: {e}")
        return False

def check_environment():
    """Check required environment variables."""
    print("Checking environment variables...")
    
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
        print(f"✗ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running tests.")
        return False
    else:
        print("✓ All required environment variables are set")
        return True

async def main():
    """Run all tests."""
    print("MAGPIE Databricks MCP Server Test Suite")
    print("=" * 50)
    
    # Check environment first
    if not check_environment():
        print("\nTest suite cannot continue without proper environment configuration.")
        sys.exit(1)
    
    tests = [
        test_configuration,
        test_authentication,
        test_api_clients,
        test_server_initialization,
        test_basic_api_call,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The Databricks MCP server is ready.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
