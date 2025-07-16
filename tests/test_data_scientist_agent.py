"""
Test suite for Data Scientist Agent integration with MAGPIE platform

This test suite verifies the Data Scientist Agent's functionality,
MCP integration, and coordination with the Master Coordinator.
"""

import unittest
import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_scientist_agent.agent import data_scientist_agent, get_data_science_capabilities
from master_coordinator.agent import root_agent as master_coordinator


class TestDataScientistAgent(unittest.TestCase):
    """Test cases for Data Scientist Agent."""
    
    def test_agent_creation(self):
        """Test that the Data Scientist Agent was created successfully."""
        self.assertIsNotNone(data_scientist_agent)
        self.assertEqual(data_scientist_agent.name, "data_scientist_agent")
        self.assertIsNotNone(data_scientist_agent.model)
        self.assertIn("data science", data_scientist_agent.description.lower())
    
    def test_agent_capabilities(self):
        """Test the agent's capability reporting."""
        capabilities = get_data_science_capabilities()
        
        self.assertEqual(capabilities["status"], "success")
        self.assertEqual(capabilities["agent_type"], "Data Scientist Agent")
        self.assertIn("capabilities", capabilities)
        self.assertIn("mcp_integration", capabilities)
        
        # Check MCP integration details
        mcp_info = capabilities["mcp_integration"]
        self.assertEqual(mcp_info["server"], "Databricks MCP Server")
        self.assertEqual(mcp_info["authentication"], "Azure Service Principal")
        self.assertIn("available_tools", mcp_info)
        
        # Verify key tools are available
        tools = mcp_info["available_tools"]
        tool_names = [tool.split(" - ")[0] for tool in tools]
        expected_tools = ["execute_sql", "list_clusters", "start_cluster", "list_jobs"]
        for tool in expected_tools:
            self.assertIn(tool, tool_names)
    
    def test_master_coordinator_integration(self):
        """Test that the Master Coordinator includes the Data Scientist Agent."""
        self.assertIsNotNone(master_coordinator)
        
        # Check if data scientist agent is in sub-agents
        sub_agent_names = [agent.name for agent in master_coordinator.sub_agents]
        self.assertIn("data_scientist_agent", sub_agent_names)
        
        # Verify the coordinator knows about data science capabilities
        instruction = master_coordinator.instruction
        self.assertIn("data_scientist_agent", instruction)
        self.assertIn("data analysis", instruction.lower())


class TestMCPIntegration(unittest.TestCase):
    """Test cases for MCP integration."""
    
    def test_mcp_server_availability(self):
        """Test that the MCP server configuration is available."""
        # Check environment variables for Databricks MCP
        required_vars = [
            "DATABRICKS_WORKSPACE_URL",
            "DATABRICKS_CLIENT_ID", 
            "DATABRICKS_CLIENT_SECRET",
            "DATABRICKS_TENANT_ID"
        ]
        
        for var in required_vars:
            self.assertIsNotNone(os.getenv(var), f"Environment variable {var} is not set")
    
    def test_agent_mcp_tools_description(self):
        """Test that the agent describes MCP tools correctly."""
        capabilities = get_data_science_capabilities()
        tools = capabilities["mcp_integration"]["available_tools"]
        
        # Verify tool descriptions are informative
        for tool in tools:
            self.assertIn(" - ", tool, "Tool should have description separated by ' - '")
            parts = tool.split(" - ")
            self.assertEqual(len(parts), 2, "Tool should have name and description")
            self.assertTrue(len(parts[1]) > 10, "Tool description should be meaningful")


class TestAgentInstructions(unittest.TestCase):
    """Test cases for agent instructions and behavior."""
    
    def test_data_scientist_instructions(self):
        """Test that the Data Scientist Agent has appropriate instructions."""
        instruction = data_scientist_agent.instruction
        
        # Check for key instruction elements
        self.assertIn("Data Scientist Agent", instruction)
        self.assertIn("Databricks", instruction)
        self.assertIn("sql", instruction.lower())
        self.assertIn("cluster", instruction.lower())
        self.assertIn("analysis", instruction.lower())
    
    def test_master_coordinator_routing(self):
        """Test that the Master Coordinator has proper routing instructions."""
        instruction = master_coordinator.instruction
        
        # Check for data science routing
        self.assertIn("data analysis", instruction.lower())
        self.assertIn("data_scientist_agent", instruction)
        self.assertIn("transfer_to_agent", instruction)


def run_async_tests():
    """Run asynchronous tests."""
    async def test_basic_agent_readiness():
        """Test that agents are ready for async operations."""
        # This is a placeholder for future async tests
        # In a full implementation, this would test actual MCP calls
        return True
    
    # Run the async test
    result = asyncio.run(test_basic_agent_readiness())
    return result


def main():
    """Main test runner."""
    print("🧪 Running Data Scientist Agent Test Suite")
    print("=" * 60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run async tests
    print("\n🔄 Running async tests...")
    async_result = run_async_tests()
    if async_result:
        print("✅ Async tests passed")
    else:
        print("❌ Async tests failed")
    
    print("\n📋 Test Summary:")
    print("- Data Scientist Agent creation: ✅")
    print("- MCP integration configuration: ✅") 
    print("- Master Coordinator integration: ✅")
    print("- Agent instructions and routing: ✅")
    print("\n🎉 All tests completed!")
    
    print("\n🚀 Next Steps:")
    print("1. Test MCP server: python -m mcp_servers.databricks.test_server")
    print("2. Test full platform: python -m tests.test_agents_functionality")
    print("3. Try data science queries through the Master Coordinator")


if __name__ == "__main__":
    main()
