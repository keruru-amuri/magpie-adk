# Data Scientist Agent

A specialized agent for data science tasks that integrates with Databricks through the MAGPIE platform's centralized MCP server infrastructure.

## Overview

The Data Scientist Agent is designed to help users perform data analysis, exploration, and business intelligence tasks using Databricks as the computational backend. It leverages the centralized MCP (Model Context Protocol) server infrastructure to provide secure, efficient access to Databricks resources.

## Features

### Core Capabilities
- **Data Analysis**: Execute SQL queries for data exploration and analysis
- **Cluster Management**: Manage Databricks clusters for computational resources
- **Job Execution**: Run data processing workflows and jobs
- **Business Intelligence**: Provide insights and recommendations based on data analysis

### MCP Integration
- **Centralized Access**: Uses the Databricks MCP server for all Databricks operations
- **Service Principal Authentication**: Secure authentication through Azure AD
- **Agent-Agnostic Design**: Shares MCP infrastructure with other MAGPIE agents

## Architecture

```
Data Scientist Agent
        │
        ▼
Centralized MCP Server (Databricks)
        │
        ▼
Databricks Workspace
```

## Available Tools (via MCP)

### Data Operations
- `execute_sql` - Execute SQL statements for data analysis
- `list_warehouses` - View available SQL warehouses

### Cluster Management
- `list_clusters` - View available computational clusters
- `get_cluster` - Get detailed cluster information
- `start_cluster` - Start clusters for data processing
- `terminate_cluster` - Stop clusters when not needed

### Job Management
- `list_jobs` - View available data processing jobs
- `get_job` - Get detailed job information
- `run_job` - Execute data processing workflows

## Usage Examples

### Data Exploration
```
"Show me the schema of the customer_data table"
"What are the top 10 products by sales volume?"
"Analyze the distribution of customer ages"
```

### Data Quality Assessment
```
"Check for null values in the orders table"
"Find duplicate records in customer data"
"Identify outliers in the sales data"
```

### Business Intelligence
```
"Calculate monthly revenue trends"
"Analyze customer segmentation patterns"
"Compare performance across different regions"
```

### Cluster Management
```
"Show me available clusters"
"Start the analytics cluster"
"Check cluster status and performance"
```

## Configuration

The agent uses the same environment configuration as other MAGPIE agents:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AZURE_OPENAI_API_VERSION=your-api-version

# Databricks Configuration (for MCP server)
DATABRICKS_WORKSPACE_URL=https://your-workspace.azuredatabricks.net
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-secret
DATABRICKS_TENANT_ID=your-azure-tenant-id
```

## Model Configuration

The agent supports multi-model configuration through the MAGPIE model factory:

- **Default**: Uses `DATA_SCIENTIST_AGENT_MODEL` environment variable
- **Fallback**: Uses `gpt-4.1-mini` for cost-effective data analysis
- **Recommended**: `gpt-4.1` or `DeepSeek-R1` for complex analytical tasks

## Integration with MAGPIE Platform

### Master Coordinator Integration
The Data Scientist Agent can be integrated with the Master Coordinator for intelligent routing of data science requests.

### Shared MCP Infrastructure
- Uses the same Databricks MCP server as other agents
- Benefits from centralized authentication and connection management
- Consistent API access patterns across the platform

## Testing

To test the agent's MCP integration:

```bash
# Test the Databricks MCP server
python -m mcp_servers.databricks.test_server

# Test the agent (when integrated with test framework)
python -m tests.test_data_scientist_agent
```

## Best Practices

### Data Analysis
1. Always understand the data context before analysis
2. Use appropriate SQL queries for the task
3. Explain findings in business-friendly language
4. Suggest follow-up analyses when relevant

### Resource Management
1. Check cluster availability before intensive operations
2. Start clusters only when needed
3. Monitor resource usage and costs
4. Terminate clusters after use to save costs

### Security
1. Use service principal authentication
2. Follow data access policies
3. Handle sensitive data appropriately
4. Log all data access for audit purposes

## Future Enhancements

- **Advanced Analytics**: Integration with MLflow for machine learning workflows
- **Data Visualization**: Support for generating charts and graphs
- **Automated Insights**: AI-powered pattern detection and recommendations
- **Collaboration**: Integration with notebook sharing and collaboration features

## Support

For issues related to:
- **Agent functionality**: Check the MAGPIE platform documentation
- **MCP integration**: Refer to `docs/CENTRALIZED_MCP_INFRASTRUCTURE.md`
- **Databricks connectivity**: Check the Databricks MCP server logs
- **Authentication**: Verify Azure service principal configuration
