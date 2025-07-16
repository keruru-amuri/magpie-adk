# MAGPIE MCP Server Quick Start Guide

**For New Augment Code Sessions**

This guide provides everything you need to understand and work with the MAGPIE platform's centralized Model Context Protocol (MCP) server infrastructure.

## 🎯 **What You Need to Know**

### **Current State**
- ✅ **Centralized MCP infrastructure implemented** in `mcp_servers/` directory
- ✅ **Databricks MCP server fully functional** with Azure service principal authentication
- ✅ **All tests passing** - server is production-ready
- ✅ **Agent-agnostic design** - multiple agents can consume the same MCP servers

### **Key Files**
```
mcp_servers/databricks/
├── config.py              # Service principal configuration
├── auth.py                 # Azure AD authentication
├── server.py               # Main MCP server implementation
├── test_server.py          # Test suite (5/5 tests passing)
├── start_server.py         # Startup script
└── api/                    # API client modules
    ├── base.py             # Base API client
    ├── clusters.py         # Clusters API
    ├── jobs.py             # Jobs API
    └── sql.py              # SQL API
```

## 🔧 **Configuration**

### **Environment Variables**
The server automatically loads from the **root `.env` file**:

```bash
# Databricks Configuration (automatically mapped from existing variables)
DATABRICKS_WORKSPACE_URL=https://your-workspace.azuredatabricks.net
DATABRICKS_CLIENT_ID=your-service-principal-client-id
DATABRICKS_CLIENT_SECRET=your-service-principal-secret
DATABRICKS_TENANT_ID=your-azure-tenant-id

# Optional
DATABRICKS_WAREHOUSE_ID=your-warehouse-id
LOG_LEVEL=INFO
SERVER_PORT=8000
```

### **Authentication Model**
- **Service Principal Authentication** (not PAT)
- **OAuth 2.0 client credentials flow**
- **Automatic token refresh**
- **Azure AD integration**

## 🚀 **Running the Server**

### **Test the Server**
```bash
# From project root - all tests should pass
python -m mcp_servers.databricks.test_server
```

### **Start the Server**
```bash
# Option 1: Direct execution
python -m mcp_servers.databricks.server

# Option 2: Using startup script
python mcp_servers/databricks/start_server.py
```

## 🛠️ **Available MCP Tools**

### **Cluster Management**
- `list_clusters` - List all Databricks clusters
- `get_cluster` - Get cluster information by ID
- `create_cluster` - Create new clusters
- `start_cluster` - Start terminated clusters  
- `terminate_cluster` - Terminate running clusters

### **Job Management**
- `list_jobs` - List all Databricks jobs
- `get_job` - Get job information by ID
- `run_job` - Execute jobs immediately

### **SQL Operations**
- `execute_sql` - Execute SQL statements
- `list_warehouses` - List SQL warehouses

## 🔌 **Agent Integration**

### **How Agents Consume the MCP Server**
```python
# Example agent integration
async def query_databricks(self, sql_statement: str):
    """Query Databricks using centralized MCP server."""
    result = await self.mcp_client.call_tool(
        "execute_sql", 
        {"statement": sql_statement}
    )
    return result
```

### **Current Agent Support**
- ✅ **Engineering Process Procedure Agent** - Can consume Databricks tools
- ✅ **Future Data Scientist Agent** - Ready for integration
- ✅ **Any MAGPIE Agent** - Agent-agnostic design

## 🏗️ **Architecture**

```
MAGPIE Agents ──▶ Centralized MCP Servers ──▶ External Services
     │                      │                        │
     ├─ Engineering         ├─ Databricks MCP        ├─ Databricks
     ├─ Data Science        ├─ Future Azure MCP      ├─ Azure
     └─ General Chat        └─ Future AWS MCP        └─ AWS
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Import Errors**
   - Run from project root: `python -m mcp_servers.databricks.test_server`
   - All imports use absolute paths

2. **Authentication Failures**
   - Check environment variables are set
   - Verify service principal has Databricks access
   - Check Azure AD tenant ID

3. **Port Conflicts**
   - Set `SERVER_PORT` environment variable
   - Default uses stdio transport (no ports needed)

### **Test Results Should Show**
```
✓ All required environment variables are set
✓ Configuration loaded successfully  
✓ Authentication successful
✓ API clients initialized successfully
✓ MCP server initialized successfully
✓ Basic API call successful
🎉 All tests passed! The Databricks MCP server is ready.
```

## 📖 **Additional Documentation**

- **`docs/CENTRALIZED_MCP_INFRASTRUCTURE.md`** - Complete architecture guide
- **`mcp_servers/databricks/README.md`** - Databricks server details
- **`docs/MCP_IMPLEMENTATION_SUMMARY.md`** - Implementation overview

## 🎯 **For New Sessions**

### **Key Points to Remember**
1. **MCP infrastructure is fully implemented and tested**
2. **Uses existing Azure service principal credentials**
3. **Agent-agnostic design for platform scalability**
4. **Production-ready with comprehensive error handling**
5. **No containers required - runs as standard Python process**

### **Quick Validation**
```bash
# Verify everything works
python -m mcp_servers.databricks.test_server
# Should show: "🎉 All tests passed! The Databricks MCP server is ready."
```

### **Next Steps**
- Integrate with existing agents
- Add more MCP tools as needed
- Implement additional MCP servers (Azure, AWS, etc.)
- Scale to production workloads

---

**Status**: ✅ **PRODUCTION READY** - All tests passing, fully functional MCP infrastructure
