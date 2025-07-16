"""
Data Scientist Agent MCP Integration Demo

This script demonstrates how the Data Scientist Agent integrates with
the centralized MCP server infrastructure for Databricks operations.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_scientist_agent.agent import data_scientist_agent, get_data_science_capabilities


def display_agent_info():
    """Display information about the Data Scientist Agent."""
    print("🤖 Data Scientist Agent Information")
    print("=" * 50)
    
    print(f"Agent Name: {data_scientist_agent.name}")
    print(f"Model: {data_scientist_agent.model}")
    print(f"Description: {data_scientist_agent.description}")
    
    capabilities = get_data_science_capabilities()
    print(f"\nAgent Type: {capabilities['agent_type']}")
    print(f"Architecture: {capabilities['architecture']}")
    
    print("\nCore Capabilities:")
    for capability in capabilities['capabilities']:
        print(f"  • {capability}")


def display_mcp_integration():
    """Display MCP integration details."""
    print("\n🔌 MCP Integration Details")
    print("=" * 50)
    
    capabilities = get_data_science_capabilities()
    mcp_info = capabilities['mcp_integration']
    
    print(f"MCP Server: {mcp_info['server']}")
    print(f"Authentication: {mcp_info['authentication']}")
    
    print("\nAvailable MCP Tools:")
    for tool in mcp_info['available_tools']:
        print(f"  • {tool}")


def display_sample_workflows():
    """Display sample data science workflows."""
    print("\n📊 Sample Data Science Workflows")
    print("=" * 50)
    
    workflows = [
        {
            "name": "Data Exploration Workflow",
            "steps": [
                "1. List available clusters: 'Show me available clusters'",
                "2. Start analytics cluster: 'Start the analytics cluster'", 
                "3. Explore data: 'Show me the schema of the sales_data table'",
                "4. Basic analysis: 'What are the top 10 products by revenue?'"
            ]
        },
        {
            "name": "Data Quality Assessment",
            "steps": [
                "1. Check data completeness: 'Check for null values in customer_data'",
                "2. Find duplicates: 'Identify duplicate records in orders table'",
                "3. Outlier detection: 'Find outliers in the sales amounts'",
                "4. Data validation: 'Validate email formats in customer table'"
            ]
        },
        {
            "name": "Business Intelligence Analysis",
            "steps": [
                "1. Trend analysis: 'Calculate monthly revenue trends for 2024'",
                "2. Segmentation: 'Analyze customer segments by purchase behavior'",
                "3. Performance metrics: 'Compare sales performance across regions'",
                "4. Forecasting: 'Predict next quarter sales based on trends'"
            ]
        }
    ]
    
    for workflow in workflows:
        print(f"\n{workflow['name']}:")
        for step in workflow['steps']:
            print(f"  {step}")


def display_mcp_architecture():
    """Display the MCP architecture diagram."""
    print("\n🏗️ MCP Architecture")
    print("=" * 50)
    
    architecture = """
    Data Scientist Agent
            │
            ▼
    ┌─────────────────────────────────┐
    │   Centralized MCP Server        │
    │   (Databricks Integration)      │
    │                                 │
    │   • Service Principal Auth      │
    │   • Automatic Token Refresh     │
    │   • Agent-Agnostic Design       │
    │   • Comprehensive Error         │
    │     Handling                    │
    └─────────────────────────────────┘
            │
            ▼
    ┌─────────────────────────────────┐
    │   Databricks Workspace         │
    │                                 │
    │   • Clusters & Compute          │
    │   • SQL Warehouses              │
    │   • Jobs & Workflows            │
    │   • Data & Analytics            │
    └─────────────────────────────────┘
    """
    
    print(architecture)


def display_testing_instructions():
    """Display instructions for testing the MCP integration."""
    print("\n🧪 Testing MCP Integration")
    print("=" * 50)
    
    print("To test the MCP integration:")
    print("\n1. Test MCP Server:")
    print("   python -m mcp_servers.databricks.test_server")
    
    print("\n2. Test Agent Creation:")
    print("   python data_scientist_agent/test_agent.py")
    
    print("\n3. Test Full Platform Integration:")
    print("   python tests/test_data_scientist_agent.py")
    
    print("\n4. Test with Master Coordinator:")
    print("   # Start the MAGPIE platform and ask:")
    print("   # 'Show me available Databricks clusters'")
    print("   # 'Analyze the sales data for trends'")
    print("   # 'What's the data quality of our customer table?'")
    
    print("\n5. Environment Requirements:")
    print("   Ensure these environment variables are set:")
    env_vars = [
        "DATABRICKS_WORKSPACE_URL",
        "DATABRICKS_CLIENT_ID", 
        "DATABRICKS_CLIENT_SECRET",
        "DATABRICKS_TENANT_ID",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT"
    ]
    for var in env_vars:
        status = "✅" if os.getenv(var) else "❌"
        print(f"   {status} {var}")


async def demo_agent_interaction():
    """Demonstrate basic agent interaction (without actual MCP calls)."""
    print("\n🎭 Agent Interaction Demo")
    print("=" * 50)
    
    print("This demo shows how the agent would handle different types of queries:")
    
    sample_queries = [
        "Show me available Databricks clusters",
        "Execute SQL: SELECT COUNT(*) FROM sales_data",
        "Analyze customer segmentation patterns",
        "Check data quality in the orders table"
    ]
    
    for query in sample_queries:
        print(f"\n📝 User Query: '{query}'")
        print("🤖 Agent Response: [Would process through MCP server]")
        print("   → Route to appropriate Databricks tool")
        print("   → Execute via centralized MCP infrastructure")
        print("   → Return formatted results to user")
        
        # Simulate processing time
        await asyncio.sleep(0.5)
    
    print("\n✨ In a full implementation, these would be actual MCP tool calls!")


def main():
    """Main demo function."""
    print("🚀 Data Scientist Agent MCP Integration Demo")
    print("=" * 60)
    
    # Display agent information
    display_agent_info()
    
    # Display MCP integration details
    display_mcp_integration()
    
    # Display sample workflows
    display_sample_workflows()
    
    # Display architecture
    display_mcp_architecture()
    
    # Run async demo
    print("\n🔄 Running interaction demo...")
    asyncio.run(demo_agent_interaction())
    
    # Display testing instructions
    display_testing_instructions()
    
    print("\n🎉 Demo completed!")
    print("\nThe Data Scientist Agent is ready for MCP integration!")
    print("Next step: Integrate with actual MCP client for live Databricks operations.")


if __name__ == "__main__":
    main()
