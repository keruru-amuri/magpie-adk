"""
Data Scientist Agent for MAGPIE Platform

A specialized agent for data science tasks that integrates with Databricks
through the centralized MCP server infrastructure.
"""

import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Import model factory for multi-model support
from common.model_factory import create_model_for_agent

# Import MCP client tools
from .mcp_client import list_clusters_sync, get_cluster_sync, execute_sql_sync

# Load environment variables from .env file
load_dotenv()

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Set LiteLLM environment variables for Azure OpenAI
os.environ["AZURE_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = AZURE_OPENAI_API_VERSION


def get_data_science_capabilities() -> dict:
    """Returns information about the Data Scientist Agent's capabilities.
    
    Returns:
        dict: Information about the agent's capabilities
    """
    return {
        "status": "success",
        "agent_type": "Data Scientist Agent",
        "architecture": "Single agent with MCP integration",
        "capabilities": [
            "Data analysis and exploration using Databricks",
            "SQL query execution for data insights",
            "Cluster management for computational resources",
            "Job execution for data processing workflows",
            "Integration with centralized MCP server infrastructure",
            "Service principal authentication for secure Databricks access"
        ],
        "mcp_integration": {
            "server": "Databricks MCP Server",
            "authentication": "Azure Service Principal",
            "available_tools": [
                "execute_sql - Execute SQL statements for data analysis",
                "list_clusters - View available computational resources",
                "get_cluster - Get detailed cluster information",
                "start_cluster - Start clusters for data processing",
                "list_jobs - View available data processing jobs",
                "run_job - Execute data processing workflows",
                "list_warehouses - View available SQL warehouses"
            ]
        },
        "use_cases": [
            "Exploratory data analysis",
            "Data quality assessment",
            "Statistical analysis and reporting",
            "Data pipeline monitoring",
            "Performance optimization queries",
            "Business intelligence insights"
        ]
    }


def get_sample_queries() -> dict:
    """Provides sample data science queries and use cases.
    
    Returns:
        dict: Sample queries and examples
    """
    return {
        "status": "success",
        "sample_queries": [
            {
                "category": "Data Exploration",
                "examples": [
                    "Show me the schema of the customer_data table",
                    "What are the top 10 products by sales volume?",
                    "Analyze the distribution of customer ages"
                ]
            },
            {
                "category": "Data Quality",
                "examples": [
                    "Check for null values in the orders table",
                    "Find duplicate records in customer data",
                    "Identify outliers in the sales data"
                ]
            },
            {
                "category": "Business Intelligence",
                "examples": [
                    "Calculate monthly revenue trends",
                    "Analyze customer segmentation patterns",
                    "Compare performance across different regions"
                ]
            },
            {
                "category": "Cluster Management",
                "examples": [
                    "Show me available clusters",
                    "Start the analytics cluster",
                    "Check cluster status and performance"
                ]
            }
        ]
    }


# Create the data scientist agent
try:
    # Use the model factory to get the appropriate model for this agent
    model = create_model_for_agent('data_scientist_agent')
    
    data_scientist_agent = LlmAgent(
        name="data_scientist_agent",
        model=model,
        description="Specialized agent for data science tasks using Databricks through centralized MCP infrastructure. "
                   "Handles data analysis, SQL queries, cluster management, and business intelligence insights.",
        instruction="""You are a Data Scientist Agent specialized in data analysis and insights using Databricks.

Your primary capabilities include:
1. **Data Analysis**: Execute SQL queries to explore and analyze data
2. **Cluster Management**: Manage Databricks clusters for computational resources
3. **Job Execution**: Run data processing workflows and jobs
4. **Business Intelligence**: Provide insights and recommendations based on data

You have access to Databricks through a centralized MCP server with the following tools:
- list_clusters_sync: View available computational clusters
- get_cluster_sync: Get detailed information about specific clusters
- execute_sql_sync: Run SQL queries for data analysis

When users ask for data analysis:
1. First understand what they want to analyze
2. Use appropriate SQL queries to extract insights
3. Explain your findings in clear, business-friendly language
4. Suggest follow-up analyses when relevant

For cluster management:
1. Check cluster availability before running intensive queries
2. Start clusters when needed for better performance
3. Provide status updates on cluster operations

Always prioritize data accuracy and provide context for your analyses.
Be helpful in explaining technical concepts in accessible terms.""",
        tools=[list_clusters_sync, get_cluster_sync, execute_sql_sync]
    )
    
    print(f"✅ Data Scientist Agent created successfully using model: {model}")
    
except Exception as e:
    print(f"❌ Failed to create Data Scientist Agent: {e}")
    # Create a fallback agent without model factory
    from google.adk.models.lite_llm import LiteLlm
    
    fallback_model = LiteLlm(model="azure/gpt-4.1-mini")
    
    data_scientist_agent = LlmAgent(
        name="data_scientist_agent",
        model=fallback_model,
        description="Specialized agent for data science tasks using Databricks through centralized MCP infrastructure.",
        instruction="You are a Data Scientist Agent. Help users with data analysis using Databricks tools."
    )
    
    print(f"⚠️ Created fallback Data Scientist Agent using: {fallback_model}")
