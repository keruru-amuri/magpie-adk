# MAGPIE (MAG Platform for Intelligent Execution) with Google ADK and Azure OpenAI

This project implements the MAGPIE platform - a sophisticated multi-agent platform designed to support various types of agents using Google Agent Development Kit (ADK) with Azure OpenAI models via LiteLLM. The platform features a master coordinator that intelligently routes requests to specialized sub-agents.

## Features

- **Multi-Agent Architecture**: Master coordinator with specialized sub-agents
- **Google ADK Integration**: Uses Google's Agent Development Kit for agent orchestration
- **Multi-Model Support**: Choose from 4 Azure models (GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, DeepSeek-R1-0528)
- **Agent-Specific Models**: Each agent can use a different model optimized for its tasks
- **Intelligent Routing**: LLM-driven delegation between specialized agents
- **Specialized Agents**: Engineering process procedure agent with aviation query enhancement, and general conversation agents
- **Databricks Integration**: Engineering process procedure agent with service principal authentication and automatic query enhancement
- **Agent Transfer System**: Seamless handoffs between specialist agents
- **Web Interface**: Provides a web-based chat interface via `adk web`

## Prerequisites

- Python 3.8+
- Azure OpenAI account with model deployments (GPT-4.1, GPT-4.1-mini, GPT-4.1-nano, DeepSeek-R1-0528)
- Valid Azure OpenAI API credentials
- Databricks workspace with serving endpoints (for engineering knowledge agent)
- Azure service principal for Databricks authentication

## Tag Information

- [db] stands for DataBricks.

## Configuration

The project uses environment variables defined in `.env`:

```env
# MAGPIE Platform Configuration Template
# Copy this file to .env and fill in your actual values
#
# This configuration supports:
# - Master Coordinator (intelligent routing)
# - Engineering Process Procedure Agent [db] (Databricks technical queries)
# - General Chat Agent (conversations & advice)
# - Multi-Model Support (4 different Azure models)

# Azure OpenAI API Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Multi-Model Configuration
# Available Models: gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, DeepSeek-R1-0528
AVAILABLE_MODELS_GPT41=azure/gpt-4.1
AVAILABLE_MODELS_GPT41_MINI=azure/gpt-4.1-mini
AVAILABLE_MODELS_GPT41_NANO=azure/gpt-4.1-nano
AVAILABLE_MODELS_DEEPSEEK=azure/DeepSeek-R1-0528

# Agent-Specific Model Configuration
MASTER_COORDINATOR_MODEL=azure/gpt-4.1
ENGINEERING_PROCESS_AGENT_MODEL=azure/DeepSeek-R1-0528
GENERAL_CHAT_AGENT_MODEL=azure/gpt-4.1-mini

# Legacy Configuration (backward compatibility)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_MODEL=azure/gpt-4.1

# ADK Configuration
# Disable Vertex AI to use direct API keys
GOOGLE_GENAI_USE_VERTEXAI=False

# Model Selection Strategy
MODEL_SELECTION_STRATEGY=agent_specific

# Databricks Configuration (for Engineering Process Procedure Agent and MCP Server)
# Required for service principal authentication to Databricks APIs
#
# How to obtain these values:
# 1. DATABRICKS_WORKSPACE_URL: Your Databricks workspace URL (e.g., https://adb-123456789.11.azuredatabricks.net)
# 2. DATABRICKS_TENANT_ID: Azure AD tenant ID where your service principal is registered
# 3. DATABRICKS_CLIENT_ID: Service principal application (client) ID
# 4. DATABRICKS_CLIENT_SECRET: Service principal client secret
#
# Note: The service principal must have access to Databricks APIs and serving endpoints
DATABRICKS_WORKSPACE_URL=https://your-databricks-workspace.azuredatabricks.net
DATABRICKS_TENANT_ID=your_azure_tenant_id
DATABRICKS_CLIENT_ID=your_service_principal_client_id
DATABRICKS_CLIENT_SECRET=your_service_principal_secret

# Optional: Default warehouse for SQL operations
DATABRICKS_WAREHOUSE_ID=your_warehouse_id

# MAGPIE Platform Configuration
DEFAULT_LLM_MODEL=azure/gpt-4.1
DEFAULT_TEMPERATURE=0.2
DEFAULT_MAX_TOKENS=1000

# Logging Configuration
AGENT_LOG_LEVEL=INFO
LITELLM_DEBUG=False
```

## Multi-Model Support

The MAGPIE platform supports 4 different Azure models, allowing each agent to use the most suitable model for its specific tasks:

| Model | Use Case | Characteristics |
|-------|----------|-----------------|
| **GPT-4.1** | Complex reasoning, routing decisions | High capability, higher cost |
| **GPT-4.1 Mini** | General conversation, casual chat | Balanced capability/cost |
| **GPT-4.1 Nano** | Focused tasks, query enhancement | Fast, cost-effective |
| **DeepSeek-R1-0528** | Technical queries, reasoning | 128K context, strong reasoning |

### Model Selection Strategies

- **`agent_specific`** (Recommended): Each agent uses its configured model
- **`default`**: All agents use the same default model
- **`environment`**: Legacy single-model mode

### Validation

Test your multi-model configuration:

```bash
python validate_multi_model_config.py
```

For detailed configuration guide, see [MULTI_MODEL_CONFIGURATION_GUIDE.md](MULTI_MODEL_CONFIGURATION_GUIDE.md).

## Installation

### Option 1: Automated Setup

Run the setup script:

```bash
python setup.py
```

### Option 2: Manual Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Unix/Linux/macOS
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Test the Agent

```bash
python agents.py
```

### 2. Start Web Interface

```bash
adk web
```

Then open http://localhost:8000 in your browser.

### 3. Interact with the Multi-Agent System

The platform automatically routes your requests to the appropriate specialist agent:

#### Technical & Engineering Questions (→ engineering_process_procedure_agent)
- **Aviation MRO**: "What is the process of component robbing?"
- **Aircraft maintenance**: "How do I perform a C-check inspection?"
- **Engineering procedures**: "What are the regulatory requirements for engine overhaul?"
- **RAG-powered responses**: Leverages Databricks serving endpoints with aviation knowledge

#### General Conversation (→ general_chat_agent)
- **General chat**: "How are you today?"
- **Advice**: "Can you give me some motivation?"
- **Creative help**: "Help me brainstorm ideas"
- **Casual conversation**: "Tell me something interesting"

#### System Information (→ master_coordinator)
- **System status**: "What agents are available?"
- **Routing help**: "How does the routing work?"

The master coordinator intelligently analyzes your request and routes it to the most appropriate specialist agent automatically.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MAGPIE Platform for Intelligent Execution               │
├─────────────────────────────────────────────────────────────────────────────┤
│                          Master Coordinator                                │
│                     (LLM-Driven Delegation)                                │
├─────────────────────────────────┬───────────────────────────────────────────┤
│ Engineering Process Procedure   │      General Chat Agent                  │
│         Agent [db]              │                                           │
│ ┌─────────────────────────────┐ │ ┌─────────────────────────────────────┐ │
│ │• Databricks Queries         │ │ │• General Conversation               │ │
│ │• Engineering Data           │ │ │• Advice & Motivation                │ │
│ │• Technical Docs             │ │ │• Creative Help                      │ │
│ │• RAG Models                 │ │ │• Casual Chat                        │ │
│ │• Service Principal          │ │ └─────────────────────────────────────┘ │
│ └─────────────────────────────┘ │                                           │
└─────────────────────────────────┴───────────────────────────────────────────┘
                                      │
                    ┌──────────────┐  │  ┌─────────────────┐
                    │   LiteLLM    │──┼─▶│  Azure OpenAI   │
                    │  (Proxy)     │  │  │   (GPT-4.1)     │
                    └──────────────┘  │  └─────────────────┘
                                      │
                                      │  ┌─────────────────┐
                                      └─▶│   Databricks    │
                                         │ Serving Endpoints│
                                         └─────────────────┘
```

## Project Structure

```
magpie-adk/
├── master_coordinator/                    # Master orchestrator agent
│   ├── __init__.py
│   └── agent.py
├── engineering_process_procedure_agent/   # Sequential agent for aviation MRO queries
│   ├── __init__.py
│   ├── agent.py
│   ├── README.md
│   └── sub_agents/
│       ├── query_enhancement_agent/       # Query enhancement subagent
│       │   ├── __init__.py
│       │   └── agent.py
│       └── databricks_query_agent/        # Databricks processing subagent
│           ├── __init__.py
│           └── agent.py
├── general_chat_agent/                    # General conversation agent
│   ├── __init__.py
│   └── agent.py
├── mcp_servers/                           # Centralized MCP servers
│   └── databricks/                        # Databricks MCP server
│       ├── __init__.py
│       ├── config.py                      # Service principal configuration
│       ├── auth.py                        # Azure AD authentication
│       ├── server.py                      # Main MCP server
│       ├── start_server.py                # Startup script
│       ├── test_server.py                 # Test suite
│       ├── requirements.txt               # MCP server dependencies
│       ├── README.md                      # Server documentation
│       └── api/                           # API client modules
│           ├── __init__.py
│           ├── base.py                    # Base API client
│           ├── clusters.py                # Clusters API
│           ├── jobs.py                    # Jobs API
│           └── sql.py                     # SQL API
├── common/                                # Shared utilities
│   ├── __init__.py
│   └── model_factory.py                  # Multi-model factory
├── docs/                                  # Detailed documentation
│   └── CENTRALIZED_MCP_INFRASTRUCTURE.md  # MCP infrastructure guide
├── tests/                                 # Test scripts
├── .env                                   # Environment configuration
├── CONFIGURATION.md                       # Multi-model configuration guide
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

## Key Components

- **`master_coordinator/`**: Central orchestrator with intelligent routing
- **`engineering_process_procedure_agent/`**: Sequential agent for aviation MRO queries with automatic enhancement and Databricks integration
- **`general_chat_agent/`**: General conversation and advice agent
- **`mcp_servers/`**: Centralized Model Context Protocol servers for external service integration
  - **`databricks/`**: Databricks MCP server with Azure service principal authentication
- **`common/`**: Shared utilities including multi-model factory
- **`docs/`**: Detailed implementation documentation including MCP infrastructure guide
- **`tests/`**: Test scripts and validation tools
- **`requirements.txt`**: Python dependencies including MCP support
- **`.env`**: Environment configuration (includes Databricks credentials)
- **`CONFIGURATION.md`**: Multi-model configuration guide

## Centralized MCP Server Infrastructure

MAGPIE now includes a centralized Model Context Protocol (MCP) server infrastructure that provides agent-agnostic access to external services:

### Architecture Benefits
- **Agent-Agnostic Design**: Multiple agents can consume the same MCP servers
- **Centralized Authentication**: Service credentials managed in one place
- **Scalability**: Easy to add new MCP servers for additional services
- **Maintainability**: Clear separation between platform and external services

### Databricks MCP Server
- **Service Principal Authentication**: Uses Azure AD instead of Personal Access Tokens
- **Comprehensive API Coverage**: Clusters, jobs, SQL, notebooks, and more
- **Multi-Agent Consumption**: Can be used by engineering, data science, and future agents

### Available Tools
- **Cluster Management**: `list_clusters`, `create_cluster`, `start_cluster`, `terminate_cluster`
- **Job Management**: `list_jobs`, `get_job`, `run_job`
- **SQL Operations**: `execute_sql`, `list_warehouses`

For detailed information, see:
- **[`docs/MCP_QUICK_START_GUIDE.md`](docs/MCP_QUICK_START_GUIDE.md)** - Quick start for new sessions
- **[`docs/CENTRALIZED_MCP_INFRASTRUCTURE.md`](docs/CENTRALIZED_MCP_INFRASTRUCTURE.md)** - Complete architecture guide

## Agent Transfer System

The system includes seamless agent-to-agent transfer capabilities:

- **Intelligent Routing**: Master coordinator automatically routes requests to appropriate specialists
- **Peer-to-Peer Transfers**: Individual agents can transfer conversations when queries fall outside their expertise
- **Context Preservation**: Transfers maintain conversation context and history

### Transfer Examples:
- General Chat agent → Engineering Process Procedure agent (for aviation MRO and technical questions)
- Engineering Process Procedure agent → General Chat agent (for casual conversation)

## Engineering Process Procedure Agent Architecture

The Engineering Process Procedure Agent implements Google ADK's Sequential Agent pattern to address tool reuse limitations:

### Architecture Overview
- **Sequential Agent Pattern**: Addresses Google ADK limitation where multiple tools cannot be effectively reused within a single agent
- **Two-Stage Pipeline**: Query Enhancement → Databricks Processing
- **Transparent Enhancement**: Users receive better responses without seeing the enhancement process

### Stage 1: Query Enhancement Subagent
- **Purpose**: Transform user queries with aviation engineering and MRO-specific context
- **Input**: Raw user query (e.g., "process of component robbing")
- **Output**: Enhanced query with aviation terminology, regulatory references (FAA/EASA), and MRO best practices
- **Function**: Acts as preprocessing layer that enriches queries with domain expertise

### Stage 2: Databricks Query Subagent
- **Purpose**: Process enhanced query and interface with Databricks LLM endpoint
- **Input**: Enhanced query from Query Enhancement Subagent
- **Output**: Contextually accurate response from aviation knowledge base
- **Function**: Handles Databricks communication and response formatting

### Technical Features
- **Service Principal Authentication**: Secure access using Azure AD service principal
- **RAG-Enabled Queries**: Leverages Databricks serving endpoints with aviation knowledge base
- **State Management**: Proper data flow between stages via ADK's output_key mechanism
- **Aviation Specialization**: Domain expertise in aircraft maintenance, regulatory compliance, and safety protocols

### Supported Model:
- `agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2`: Advanced RAG model for aviation engineering and MRO queries

## Customization

To add new tools or modify the agent:

1. Define new tool functions in `agents.py`
2. Add them to the `tools` list in the `LlmAgent` constructor
3. Update the agent description and instructions

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated and dependencies are installed
2. **Authentication errors**: Verify Azure OpenAI credentials in `.env`
3. **Model errors**: Confirm the deployment name matches your Azure OpenAI setup

### Debug Mode

Enable LiteLLM debug mode in `.env`:
```env
LITELLM_DEBUG=True
```

## Documentation & Testing

### Configuration
- **[CONFIGURATION.md](CONFIGURATION.md)** - Multi-model configuration guide

### Detailed Documentation
- **[docs/](docs/)** - Implementation details, migration summaries, and technical documentation

### Testing
- **[tests/](tests/)** - Test scripts and validation tools
- Run `python tests/validate_multi_model_config.py` to validate your configuration

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Original Blog Post](https://michaelkabuage.com/blog/13-google-adk-azure)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
