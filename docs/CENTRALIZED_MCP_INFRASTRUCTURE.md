# Centralized MCP Server Infrastructure for MAGPIE Platform

This document describes the centralized Model Context Protocol (MCP) server infrastructure implemented for the MAGPIE platform, starting with the Databricks MCP server.

## Overview

The centralized MCP infrastructure provides a scalable, agent-agnostic approach to integrating external services with the MAGPIE platform. Instead of each agent implementing its own service integrations, agents can consume shared MCP servers that provide standardized access to external APIs and services.

## Architecture

```
MAGPIE Platform Architecture with Centralized MCP Servers

┌─────────────────────────────────────────────────────────────┐
│                    MAGPIE Platform                          │
├─────────────────────────────────────────────────────────────┤
│  Agents Layer                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Master          │  │ Engineering     │  │ General     │  │
│  │ Coordinator     │  │ Process         │  │ Chat        │  │
│  │                 │  │ Procedure       │  │ Agent       │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│           │                     │                   │       │
│           └─────────────────────┼───────────────────┘       │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│  Centralized MCP Servers        │                           │
│  ┌─────────────────────────────┐ │  ┌─────────────────────┐  │
│  │ Databricks MCP Server       │ │  │ Future MCP Server   │  │
│  │ - Service Principal Auth    │ │  │ (e.g., Azure,       │  │
│  │ - Clusters, Jobs, SQL       │ │  │  AWS, GCP, etc.)    │  │
│  │ - Agent-agnostic design     │ │  │                     │  │
│  └─────────────────────────────┘ │  └─────────────────────┘  │
├─────────────────────────────────┼───────────────────────────┤
│  External Services              │                           │
│  ┌─────────────────────────────┐ │                          │
│  │ Databricks Workspace        │ │                          │
│  │ - Azure AD Authentication   │ │                          │
│  │ - Clusters & Compute        │ │                          │
│  │ - SQL Warehouses            │ │                          │
│  │ - Jobs & Workflows          │ │                          │
│  └─────────────────────────────┘ │                          │
└─────────────────────────────────────────────────────────────┘
```

## Key Benefits

### 1. **Agent-Agnostic Design**
- Multiple agents can consume the same MCP server
- Reduces code duplication across agents
- Consistent API access patterns

### 2. **Centralized Authentication**
- Service principal authentication managed in one place
- Token refresh and management handled centrally
- Enhanced security through centralized credential management

### 3. **Scalability**
- Easy to add new MCP servers for additional services
- Agents can consume multiple MCP servers as needed
- Clear separation of concerns

### 4. **Maintainability**
- Service-specific logic contained in dedicated MCP servers
- Easier to update and maintain integrations
- Clear boundaries between platform and external services

## Directory Structure

```
magpie-adk/
├── mcp_servers/                          # Centralized MCP servers
│   ├── databricks/                       # Databricks MCP server
│   │   ├── __init__.py                   # Package initialization
│   │   ├── config.py                     # Configuration with service principal auth
│   │   ├── auth.py                       # Azure AD authentication
│   │   ├── server.py                     # Main MCP server implementation
│   │   ├── start_server.py               # Startup script
│   │   ├── requirements.txt              # Dependencies
│   │   ├── README.md                     # Server documentation
│   │   └── api/                          # API client modules
│   │       ├── __init__.py
│   │       ├── base.py                   # Base API client
│   │       ├── clusters.py               # Clusters API
│   │       ├── jobs.py                   # Jobs API
│   │       └── sql.py                    # SQL API
│   └── future_servers/                   # Future MCP servers
├── agents/                               # Existing agent structure
│   ├── master_coordinator/
│   ├── engineering_process_procedure_agent/
│   └── general_chat_agent/
└── docs/
    └── CENTRALIZED_MCP_INFRASTRUCTURE.md # This document
```

## Databricks MCP Server

### Authentication Model

**Previous Approach (Reference Implementation):**
- Personal Access Token (PAT) authentication
- Tokens stored as environment variables
- Manual token management

**MAGPIE Implementation:**
- Azure service principal authentication
- OAuth 2.0 client credentials flow
- Automatic token refresh and management
- Enhanced security through Azure AD integration

### Configuration

```bash
# Required environment variables
DATABRICKS_WORKSPACE_URL=https://your-workspace.azuredatabricks.net
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-client-secret
DATABRICKS_TENANT_ID=your-azure-tenant-id

# Optional
DATABRICKS_WAREHOUSE_ID=your-default-warehouse-id
LOG_LEVEL=INFO
```

### Available Tools

#### Cluster Management
- `list_clusters`: List all clusters
- `get_cluster`: Get cluster information
- `create_cluster`: Create new clusters
- `start_cluster`: Start terminated clusters
- `terminate_cluster`: Terminate clusters

#### Job Management
- `list_jobs`: List all jobs
- `get_job`: Get job information
- `run_job`: Execute jobs immediately

#### SQL Operations
- `execute_sql`: Execute SQL statements
- `list_warehouses`: List SQL warehouses

### Agent Integration

Agents can consume the Databricks MCP server by:

1. **Configuring MCP Client**: Set up MCP client to connect to the Databricks server
2. **Tool Invocation**: Call tools using standard MCP protocol
3. **Error Handling**: Handle responses and errors appropriately

Example integration in an agent:
```python
# In agent code
async def query_databricks(self, sql_statement: str):
    """Query Databricks using centralized MCP server."""
    try:
        result = await self.mcp_client.call_tool(
            "execute_sql",
            {"statement": sql_statement}
        )
        return result
    except Exception as e:
        logger.error(f"Databricks query failed: {e}")
        raise
```

## Future Expansion

The centralized MCP infrastructure is designed to support additional services:

### Planned MCP Servers
- **Azure Services MCP Server**: Azure Resource Manager, Storage, etc.
- **AWS Services MCP Server**: EC2, S3, Lambda, etc.
- **Google Cloud MCP Server**: Compute Engine, BigQuery, etc.
- **Database MCP Server**: PostgreSQL, MySQL, MongoDB, etc.

### Implementation Guidelines

When adding new MCP servers:

1. **Follow the established pattern**: Use the Databricks server as a template
2. **Implement proper authentication**: Use appropriate auth methods for each service
3. **Agent-agnostic design**: Ensure multiple agents can consume the server
4. **Comprehensive error handling**: Implement robust error handling and logging
5. **Documentation**: Provide clear documentation and examples

## Security Considerations

### Authentication
- Use service principals or equivalent secure authentication methods
- Implement proper token refresh mechanisms
- Store credentials securely (environment variables, key vaults)

### Access Control
- Implement appropriate access controls at the service level
- Log all API calls for audit purposes
- Handle sensitive data appropriately

### Network Security
- Use HTTPS for all external API calls
- Implement proper timeout and retry mechanisms
- Handle network failures gracefully

## Monitoring and Logging

### Logging Strategy
- Comprehensive logging at all levels
- Structured logging for better analysis
- Separate log files for each MCP server
- Configurable log levels

### Monitoring
- Track API call success/failure rates
- Monitor authentication token refresh
- Alert on service availability issues
- Performance metrics for response times

## Migration from Existing Integrations

For agents with existing service integrations:

1. **Identify Integration Points**: Find where agents directly call external services
2. **Create MCP Tools**: Implement equivalent functionality in centralized MCP servers
3. **Update Agent Code**: Replace direct API calls with MCP tool invocations
4. **Test Thoroughly**: Ensure functionality is preserved
5. **Remove Old Code**: Clean up direct integration code

## Best Practices

### For MCP Server Development
- Use async/await patterns for better performance
- Implement comprehensive error handling
- Follow MCP protocol standards
- Provide clear tool descriptions and parameter schemas

### For Agent Integration
- Use MCP clients consistently across agents
- Implement proper error handling for MCP calls
- Cache results when appropriate
- Handle MCP server unavailability gracefully

## Conclusion

The centralized MCP server infrastructure provides a robust, scalable foundation for integrating external services with the MAGPIE platform. The Databricks MCP server serves as the first implementation, demonstrating the patterns and practices that will be used for future integrations.

This approach enhances the platform's maintainability, security, and scalability while providing a consistent interface for agents to access external services.
