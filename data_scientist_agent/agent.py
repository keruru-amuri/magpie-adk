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
    list_clusters_sync, get_cluster_sync, start_cluster_sync, terminate_cluster_sync, execute_sql_sync,
    list_warehouses_sync, get_warehouse_sync, start_warehouse_sync, stop_warehouse_sync,
    get_table_metadata_sync, set_table_context_sync, load_context_from_csv_sync,
    read_csv_content_sync, process_csv_for_table_context_sync, convert_schema_csv_to_context_sync
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
                "get_warehouse_sync - Get detailed warehouse information",
                "start_warehouse_sync - Start stopped SQL warehouses for queries",
                "stop_warehouse_sync - Stop running SQL warehouses to save costs",
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

**Data Analysis:**
- execute_sql_sync: Run SQL queries for data analysis

**Table Metadata Management:**
- get_table_metadata_sync: Get table metadata and context information
- set_table_context_sync: Set business context and field mappings for tables
- load_context_from_csv_sync: Load table context from CSV files

**CSV Processing (File Upload Workaround):**
- read_csv_content_sync: Read and parse CSV files when users can't upload files directly
- process_csv_for_table_context_sync: Process CSV content (as text) and apply to tables
- convert_schema_csv_to_context_sync: Convert database schema CSV files to table context format

When users ask about tables or data analysis:
1. ALWAYS start by checking table metadata (use get_table_metadata_sync)
2. If metadata exists, use it to understand business context and field meanings
3. Apply any field transformations specified in the metadata
4. Use appropriate SQL queries with proper field transformations
5. Explain your findings using business context from metadata
6. Suggest follow-up analyses when relevant

When users ask about table information (any of these patterns):
- "what do you understand/know about table X"
- "explain table X" (when not followed by SQL)
- "describe table X" (when asking for information, not SQL DESCRIBE)
- "tell me about table X"
- "show me information about table X"

Always:
1. Immediately call get_table_metadata_sync(table_name)
2. Present the business context, field mappings, and transformations
3. Explain what the table is used for based on metadata
4. Offer to run sample queries or analyses

Note: Distinguish between requests for metadata vs SQL commands by context.

For table metadata management:
1. Use get_table_metadata_sync to understand table context before querying
2. Use set_table_context_sync to add business context to tables
3. Use load_context_from_csv_sync to bulk load context from CSV files
4. Always apply field transformations based on table context

For CSV file processing (when users can't upload files):
1. If users mention they have a CSV file but can't upload it, ask them to:
   - Copy and paste the CSV content as text, OR
   - Provide the file path if it's accessible on the system
2. Use read_csv_content_sync to read CSV files from file paths
3. Use process_csv_for_table_context_sync to process CSV content provided as text
4. The system automatically detects CSV format:
   - Table context format (context_type, key, value, description)
   - Database schema format (Keys, Name, Type, Description) - converts automatically
5. Explain the workaround: "Due to file upload limitations, please paste your CSV content as text or provide the file path"

For cluster management:
1. Check cluster availability before running intensive queries
2. Start terminated clusters when needed for data processing
3. Terminate running clusters to save costs when not needed
4. Provide status updates on cluster operations
5. Help users manage computational resources efficiently

For warehouse management:
1. List available SQL warehouses before executing queries
2. Check warehouse status and configuration details
3. Start stopped warehouses when needed for SQL operations
4. Stop running warehouses to optimize costs when not in use
5. Recommend appropriate warehouse sizes for different workloads
6. Help users understand warehouse vs cluster differences

Always prioritize data accuracy and provide context for your analyses.
Be helpful in explaining technical concepts in accessible terms.""",
        tools=[
            # Cluster management tools
            list_clusters_sync, get_cluster_sync, start_cluster_sync, terminate_cluster_sync,
            # Warehouse management tools
            list_warehouses_sync, get_warehouse_sync, start_warehouse_sync, stop_warehouse_sync,
            # Data analysis tools
            execute_sql_sync,
            # Table metadata management tools
            get_table_metadata_sync, set_table_context_sync, load_context_from_csv_sync,
            # CSV processing tools (workaround for file upload limitations)
            read_csv_content_sync, process_csv_for_table_context_sync, convert_schema_csv_to_context_sync
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
