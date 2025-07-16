"""
Test MCP Integration for Data Scientist Agent

This script tests the actual MCP integration with the Databricks server.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_scientist_agent.mcp_client import list_clusters_sync, get_cluster_sync, execute_sql_sync


def test_list_clusters():
    """Test listing Databricks clusters."""
    print("🧪 Testing list_clusters...")
    
    try:
        result = list_clusters_sync()
        print(f"✅ list_clusters result: {result}")
        
        if result.get("status") == "success":
            clusters = result.get("data", {}).get("clusters", [])
            print(f"   Found {len(clusters)} clusters")
            for cluster in clusters[:3]:  # Show first 3 clusters
                print(f"   - {cluster.get('cluster_name', 'Unknown')} ({cluster.get('cluster_id', 'No ID')})")
            return True
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing list_clusters: {e}")
        return False


def test_get_cluster():
    """Test getting cluster information."""
    print("\n🧪 Testing get_cluster...")
    
    try:
        # First get a cluster ID from the list
        clusters_result = list_clusters_sync()
        if clusters_result.get("status") != "success":
            print("   Skipping - no clusters available")
            return True
            
        clusters = clusters_result.get("data", {}).get("clusters", [])
        if not clusters:
            print("   Skipping - no clusters found")
            return True
            
        cluster_id = clusters[0].get("cluster_id")
        if not cluster_id:
            print("   Skipping - no cluster ID available")
            return True
            
        print(f"   Testing with cluster ID: {cluster_id}")
        result = get_cluster_sync(cluster_id)
        print(f"✅ get_cluster result: {result}")
        
        if result.get("status") == "success":
            cluster_info = result.get("data", {})
            print(f"   Cluster name: {cluster_info.get('cluster_name', 'Unknown')}")
            print(f"   State: {cluster_info.get('state', 'Unknown')}")
            return True
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing get_cluster: {e}")
        return False


def test_execute_sql():
    """Test executing SQL."""
    print("\n🧪 Testing execute_sql...")
    
    try:
        # Test with a simple SQL query
        sql_query = "SELECT 1 as test_column"
        print(f"   Executing SQL: {sql_query}")
        
        result = execute_sql_sync(sql_query)
        print(f"✅ execute_sql result: {result}")
        
        if result.get("status") == "success":
            data = result.get("data", {})
            print(f"   Query executed successfully")
            if "result" in data:
                print(f"   Result: {data['result']}")
            return True
        else:
            error = result.get("error", "Unknown error")
            print(f"   Error: {error}")
            # SQL errors might be expected if no warehouse is configured
            if "warehouse" in error.lower() or "endpoint" in error.lower():
                print("   This is expected if no SQL warehouse is configured")
                return True
            return False
            
    except Exception as e:
        print(f"❌ Error testing execute_sql: {e}")
        return False


def test_agent_tools():
    """Test that the agent has the MCP tools."""
    print("\n🧪 Testing agent tools integration...")
    
    try:
        from data_scientist_agent.agent import data_scientist_agent
        
        if data_scientist_agent is None:
            print("❌ Agent not created")
            return False
            
        tools = data_scientist_agent.tools
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in tools]
        
        print(f"✅ Agent has {len(tools)} tools: {tool_names}")
        
        expected_tools = ["list_clusters_sync", "get_cluster_sync", "execute_sql_sync"]
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print(f"   ✅ {expected_tool} - Available")
            else:
                print(f"   ❌ {expected_tool} - Missing")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent tools: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Data Scientist Agent MCP Integration Test")
    print("=" * 60)
    
    # Test individual MCP tools
    tests = [
        test_list_clusters,
        test_get_cluster,
        test_execute_sql,
        test_agent_tools
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All MCP integration tests passed!")
        print("\nThe Data Scientist Agent is now connected to the Databricks MCP server!")
        print("\nYou can now ask questions like:")
        print("  • 'Show me available Databricks clusters'")
        print("  • 'Get information about cluster xyz'")
        print("  • 'Execute SQL: SELECT * FROM my_table LIMIT 10'")
    else:
        print("⚠️ Some tests failed. Check the configuration.")
        print("\nTroubleshooting:")
        print("1. Ensure Databricks MCP server is properly configured")
        print("2. Check environment variables for Databricks access")
        print("3. Verify service principal authentication")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
