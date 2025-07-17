# Centralized Databricks MCP Server for MAGPIE Platform

A centralized Model Context Protocol (MCP) server for Databricks that provides comprehensive access to Databricks functionality using Azure service principal authentication. This server is designed to be consumed by multiple agents across the MAGPIE platform.

## Features

- **Service Principal Authentication**: Uses Azure AD service principal instead of Personal Access Tokens (PAT)
- **Agent-Agnostic Design**: Can be consumed by multiple agents across the MAGPIE platform
- **Comprehensive API Coverage**: Supports clusters, jobs, SQL, notebooks, DBFS, and more
- **MCP Best Practices**: Follows Model Context Protocol standards and patterns
- **Google ADK Compatibility**: Designed to work with Google Agent Development Kit patterns

## Authentication

This server uses Azure service principal authentication instead of Personal Access Token (PAT) authentication. You need to configure the following environment variables:

```bash
# Databricks workspace configuration
DATABRICKS_WORKSPACE_URL=https://your-workspace.azuredatabricks.net

# Azure service principal authentication
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-client-secret
DATABRICKS_TENANT_ID=your-azure-tenant-id

# Optional: Default SQL warehouse for SQL operations
DATABRICKS_WAREHOUSE_ID=your-default-warehouse-id
```

## Available Tools

### Cluster Management
- `list_clusters`: List all Databricks clusters
- `get_cluster`: Get information about a specific cluster
- `create_cluster`: Create a new cluster
- `start_cluster`: Start a terminated cluster
- `terminate_cluster`: Terminate a cluster

### Job Management
- `list_jobs`: List all Databricks jobs
- `get_job`: Get information about a specific job
- `run_job`: Run a job immediately

### SQL Operations
- `execute_sql`: Execute SQL statements on Databricks
- `list_warehouses`: List all SQL warehouses

### Notebook Management
- `list_notebooks`: List notebooks and directories in workspace
- `get_notebook_info`: Get metadata about a notebook or workspace object
- `export_notebook`: Export a notebook from workspace in various formats
- `create_notebook`: Create a new notebook in workspace
- `import_notebook`: Import a notebook to workspace
- `delete_notebook`: Delete a notebook or directory from workspace
- `create_directory`: Create a directory in workspace
- `search_notebooks`: Search for notebooks in workspace

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create a `.env` file or set them in your environment):
```bash
DATABRICKS_WORKSPACE_URL=https://your-workspace.azuredatabricks.net
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-client-secret
DATABRICKS_TENANT_ID=your-azure-tenant-id
DATABRICKS_WAREHOUSE_ID=your-default-warehouse-id
```

## Running the Server

### Standalone Mode
```bash
python server.py
```

### As MCP Server
The server can be integrated with MCP clients by configuring it in the client's MCP configuration.

## Agent Integration

This centralized MCP server is designed to be consumed by multiple agents in the MAGPIE platform:

1. **Engineering Process Procedure Agent**: For aviation MRO queries requiring Databricks data
2. **Data Scientist Agent**: For data analysis and machine learning workflows
3. **Future Agents**: Any agent requiring Databricks functionality

## Architecture

```
MAGPIE Platform
├── Agent 1 (Engineering Process Procedure)
├── Agent 2 (Data Scientist)
├── Agent N (Future Agents)
└── Centralized MCP Servers
    ├── Databricks MCP Server (this)
    ├── Future MCP Server 1
    └── Future MCP Server N
```

## Notebook Management Features

The Databricks MCP server provides comprehensive notebook management capabilities for data scientist agents:

### Core Notebook Operations

**List Notebooks and Directories**
```json
{
  "tool": "list_notebooks",
  "params": {
    "path": "/Users/user@example.com",
    "object_type": "NOTEBOOK"
  }
}
```

**Create New Notebooks**
```json
{
  "tool": "create_notebook",
  "params": {
    "path": "/Users/user@example.com/analysis.py",
    "language": "PYTHON",
    "content": "# Data analysis notebook\nimport pandas as pd\nprint('Hello, Databricks!')"
  }
}
```

**Export Notebooks**
```json
{
  "tool": "export_notebook",
  "params": {
    "path": "/Users/user@example.com/analysis.py",
    "format": "JUPYTER",
    "direct_download": false
  }
}
```

### Advanced Features

**Search Notebooks**
- Find notebooks by name or path patterns
- Filter by workspace location
- Limit results for performance

**Import/Export Support**
- Multiple formats: SOURCE, HTML, JUPYTER, DBC, AUTO
- Base64 encoding for content transfer
- Language detection and validation

**Directory Management**
- Create workspace directories
- Recursive deletion support
- Path validation and normalization

### Use Cases for Data Scientist Agents

1. **Notebook Discovery**: Agents can explore available notebooks and understand the workspace structure
2. **Dynamic Notebook Creation**: Create analysis notebooks based on user requirements
3. **Content Analysis**: Export and analyze existing notebook content
4. **Workspace Organization**: Create directories and organize notebooks systematically
5. **Collaborative Development**: Import notebooks from external sources or export for sharing

## Security Considerations

- Uses Azure service principal authentication for enhanced security
- Supports proper token refresh and management
- Implements comprehensive error handling and logging
- Follows MCP security best practices

## Configuration

The server supports various configuration options through environment variables:

- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `SERVER_HOST`: Host to bind the server (default: 0.0.0.0)
- `SERVER_PORT`: Port to bind the server (default: 8000)
- `DEBUG`: Enable debug mode (true/false)

## Error Handling

The server implements comprehensive error handling:
- Authentication errors are properly handled and logged
- API errors include detailed error messages
- Network timeouts and retries are managed
- All errors are returned in a consistent JSON format

## Logging

Comprehensive logging is implemented:
- All API calls are logged with parameters
- Authentication events are tracked
- Errors include full stack traces
- Log level can be configured via environment variables

## Contributing

This server is part of the MAGPIE platform infrastructure. When adding new functionality:

1. Follow the existing patterns for API clients
2. Implement proper error handling
3. Add comprehensive logging
4. Update this documentation
5. Ensure agent-agnostic design principles

## License

Part of the MAGPIE Platform for Intelligent Execution.
