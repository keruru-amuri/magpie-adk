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
from .mcp_client import (
    list_clusters_sync, get_cluster_sync, execute_sql_sync,
    start_cluster_sync, terminate_cluster_sync, list_warehouses_sync,
    list_jobs_sync, get_job_sync, run_job_sync
)

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
                "execute_sql_sync - Execute SQL statements for data analysis",
                "list_clusters_sync - View available computational resources",
                "get_cluster_sync - Get detailed cluster information",
                "start_cluster_sync - Start terminated clusters for data processing",
                "terminate_cluster_sync - Stop running clusters to save resources",
                "list_warehouses_sync - View available SQL warehouses",
                "list_jobs_sync - View available data processing jobs",
                "get_job_sync - Get detailed job information",
                "run_job_sync - Execute data processing workflows"
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

**Cluster Management:**
- list_clusters_sync: View available computational clusters
- get_cluster_sync: Get detailed information about specific clusters
- start_cluster_sync: Start terminated clusters for data processing
- terminate_cluster_sync: Stop running clusters to save resources

**Data Analysis:**
- execute_sql_sync: Run SQL queries for data analysis
- list_warehouses_sync: View available SQL warehouses

**Job Management:**
- list_jobs_sync: View available data processing jobs
- get_job_sync: Get detailed job information
- run_job_sync: Execute data processing workflows

When users ask for data analysis:
1. First understand what they want to analyze
2. Check if appropriate clusters are running (use list_clusters_sync)
3. Start clusters if needed (use start_cluster_sync)
4. Use appropriate SQL queries to extract insights
5. Explain your findings in clear, business-friendly language
6. Suggest follow-up analyses when relevant

For cluster management:
1. Always check cluster status before running intensive queries
2. Start clusters when needed for better performance (use start_cluster_sync)
3. Provide status updates on cluster operations
4. Help users manage computational resources efficiently

Always prioritize data accuracy and provide context for your analyses.
Be helpful in explaining technical concepts in accessible terms.""",
        tools=[
            # Cluster management tools
            list_clusters_sync, get_cluster_sync, start_cluster_sync, terminate_cluster_sync,
            # Data analysis tools
            execute_sql_sync, list_warehouses_sync,
            # Job management tools
            list_jobs_sync, get_job_sync, run_job_sync
        ]
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
