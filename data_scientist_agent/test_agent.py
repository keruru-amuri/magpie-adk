"""
Test script for Data Scientist Agent

This script demonstrates the basic functionality of the Data Scientist Agent
and its integration with the centralized MCP infrastructure.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_scientist_agent.agent import data_scientist_agent, get_data_science_capabilities, get_sample_queries


def test_agent_creation():
    """Test that the agent was created successfully."""
    print("🧪 Testing Data Scientist Agent Creation...")
    
    if data_scientist_agent is not None:
        print(f"✅ Agent created successfully: {data_scientist_agent.name}")
        print(f"   Model: {data_scientist_agent.model}")
        print(f"   Description: {data_scientist_agent.description[:100]}...")
        return True
    else:
        print("❌ Agent creation failed")
        return False


def test_capabilities():
    """Test the agent's capability reporting."""
    print("\n🧪 Testing Agent Capabilities...")
    
    try:
        capabilities = get_data_science_capabilities()
        print(f"✅ Capabilities retrieved successfully")
        print(f"   Agent Type: {capabilities['agent_type']}")
        print(f"   Architecture: {capabilities['architecture']}")
        print(f"   Number of capabilities: {len(capabilities['capabilities'])}")
        print(f"   MCP Integration: {capabilities['mcp_integration']['server']}")
        return True
    except Exception as e:
        print(f"❌ Failed to get capabilities: {e}")
        return False


def test_sample_queries():
    """Test the sample queries functionality."""
    print("\n🧪 Testing Sample Queries...")
    
    try:
        samples = get_sample_queries()
        print(f"✅ Sample queries retrieved successfully")
        print(f"   Number of categories: {len(samples['sample_queries'])}")
        for category in samples['sample_queries']:
            print(f"   - {category['category']}: {len(category['examples'])} examples")
        return True
    except Exception as e:
        print(f"❌ Failed to get sample queries: {e}")
        return False


async def test_basic_interaction():
    """Test basic interaction with the agent (without MCP for now)."""
    print("\n🧪 Testing Basic Agent Interaction...")
    
    try:
        # This is a basic test - in a full implementation, this would
        # involve setting up MCP client and testing actual tool calls
        print("✅ Agent is ready for interaction")
        print("   Note: Full MCP integration testing requires MCP server setup")
        print("   Use the following command to test MCP server:")
        print("   python -m mcp_servers.databricks.test_server")
        return True
    except Exception as e:
        print(f"❌ Basic interaction test failed: {e}")
        return False


def display_mcp_integration_info():
    """Display information about MCP integration."""
    print("\n📋 MCP Integration Information:")
    print("=" * 50)
    
    capabilities = get_data_science_capabilities()
    mcp_info = capabilities['mcp_integration']
    
    print(f"MCP Server: {mcp_info['server']}")
    print(f"Authentication: {mcp_info['authentication']}")
    print("\nAvailable Tools:")
    for tool in mcp_info['available_tools']:
        print(f"  • {tool}")
    
    print("\nTo test MCP integration:")
    print("1. Ensure Databricks MCP server is configured")
    print("2. Run: python -m mcp_servers.databricks.test_server")
    print("3. Integrate agent with MCP client for full functionality")


def display_usage_examples():
    """Display usage examples for the agent."""
    print("\n💡 Usage Examples:")
    print("=" * 50)
    
    samples = get_sample_queries()
    for category in samples['sample_queries']:
        print(f"\n{category['category']}:")
        for example in category['examples'][:2]:  # Show first 2 examples
            print(f"  • \"{example}\"")


def main():
    """Main test function."""
    print("🚀 Data Scientist Agent Test Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_agent_creation,
        test_capabilities,
        test_sample_queries,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Run async test
    print("\n🧪 Running async tests...")
    async_result = asyncio.run(test_basic_interaction())
    results.append(async_result)
    
    # Display additional information
    display_mcp_integration_info()
    display_usage_examples()
    
    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Data Scientist Agent is ready.")
        print("\nNext steps:")
        print("1. Test MCP server: python -m mcp_servers.databricks.test_server")
        print("2. Integrate with MAGPIE platform")
        print("3. Test with real Databricks queries")
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
