# AMOS Multi-Agent System with Google ADK and Azure OpenAI

This project implements a sophisticated multi-agent system using Google Agent Development Kit (ADK) with Azure OpenAI models via LiteLLM. The system features a master coordinator that intelligently routes requests to specialized sub-agents.

## Features

- **Multi-Agent Architecture**: Master coordinator with specialized sub-agents
- **Google ADK Integration**: Uses Google's Agent Development Kit for agent orchestration
- **Azure OpenAI**: Leverages Azure OpenAI GPT-4.1 model via LiteLLM
- **Intelligent Routing**: LLM-driven delegation between specialized agents
- **Specialized Agents**: Weather/time, engineering knowledge [db], and general conversation agents
- **Databricks Integration**: Engineering knowledge agent with service principal authentication
- **Agent Transfer System**: Seamless handoffs between specialist agents
- **Web Interface**: Provides a web-based chat interface via `adk web`

## Prerequisites

- Python 3.8+
- Azure OpenAI account with GPT-4.1 deployment
- Valid Azure OpenAI API credentials
- Databricks workspace with serving endpoints (for engineering knowledge agent)
- Azure service principal for Databricks authentication

## Tag Information

- [db] stands for DataBricks.

## Configuration

The project uses environment variables defined in `.env`:

```env
# AMOS Multi-Agent System Configuration Template
# Copy this file to .env and fill in your actual values
#
# This configuration supports:
# - Master Coordinator (intelligent routing)
# - Weather Time Agent (weather & time queries)
# - Engineering Knowledge Agent [db] (Databricks technical queries)
# - General Chat Agent (conversations & advice)

# Azure OpenAI API Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# LiteLLM Azure OpenAI Model Configuration
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_MODEL=azure/gpt-4.1

# ADK Configuration
# Disable Vertex AI to use direct API keys
GOOGLE_GENAI_USE_VERTEXAI=False

# Databricks Configuration (for Engineering Knowledge Agent [db])
# Required for service principal authentication to Databricks serving endpoints
#
# How to obtain these values:
# 1. DATABRICKS_HOST: Your Databricks workspace URL (e.g., https://adb-123456789.11.azuredatabricks.net)
# 2. ARM_TENANT_ID: Azure AD tenant ID where your service principal is registered
# 3. ARM_CLIENT_ID: Service principal application (client) ID
# 4. ARM_CLIENT_SECRET: Service principal client secret
#
# Note: The service principal must have access to Databricks serving endpoints
DATABRICKS_HOST=https://your-databricks-workspace.azuredatabricks.net
ARM_TENANT_ID=your_azure_tenant_id
ARM_CLIENT_ID=your_service_principal_client_id
ARM_CLIENT_SECRET=your_service_principal_secret

# Multi-Agent System Configuration
DEFAULT_LLM_MODEL=azure/gpt-4.1
DEFAULT_TEMPERATURE=0.2
DEFAULT_MAX_TOKENS=1000

# Logging Configuration
AGENT_LOG_LEVEL=INFO
LITELLM_DEBUG=False
```

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

The system automatically routes your requests to the appropriate specialist agent:

#### Weather & Time Queries (→ weather_time_agent)
- **Weather queries**: "What's the weather in New York?"
- **Time queries**: "What time is it in Tokyo?"
- **Supported cities**: New York, London, Tokyo, Los Angeles, Paris, Sydney

#### Technical & Engineering Questions (→ engineering_knowledge_agent_db [db])
- **Engineering data**: "What are the best practices for data pipeline design?"
- **Technical documentation**: "How do I configure Databricks clusters?"
- **Knowledge base queries**: "What are the latest engineering standards?"
- **RAG-powered responses**: Leverages Databricks serving endpoints with engineering knowledge

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
│                           AMOS Multi-Agent System                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                          Master Coordinator                                │
│                     (LLM-Driven Delegation)                                │
├─────────────────┬─────────────────────────┬─────────────────────────────────┤
│ Weather Time    │ Engineering Knowledge   │      General Chat Agent        │
│     Agent       │    Agent [db]           │                                 │
│ ┌─────────────┐ │ ┌─────────────────────┐ │ ┌─────────────────────────────┐ │
│ │• Weather    │ │ │• Databricks Queries │ │ │• General Conversation       │ │
│ │• Time Zones │ │ │• Engineering Data   │ │ │• Advice & Motivation        │ │
│ │• City Info  │ │ │• Technical Docs     │ │ │• Creative Help              │ │
│ └─────────────┘ │ │• RAG Models         │ │ │• Casual Chat                │ │
│                 │ │• Service Principal  │ │ └─────────────────────────────┘ │
│                 │ └─────────────────────┘ │                                 │
└─────────────────┴─────────────────────────┴─────────────────────────────────┘
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

## Agent Structure

```
magpie-agent-adk/
├── master_coordinator/          # Master orchestrator agent
│   ├── __init__.py
│   └── agent.py
├── weather_time_agent/          # Weather & time specialist
│   ├── __init__.py
│   └── agent.py
├── engineering_knowledge_agent/ # [db] Engineering knowledge specialist
│   ├── __init__.py
│   └── agent.py
├── general_chat_agent/          # General conversation agent
│   ├── __init__.py
│   └── agent.py
├── multi_tool_agent/           # Legacy single agent (deprecated)
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Key Components

- **`master_coordinator/`**: Central orchestrator with intelligent routing
- **`weather_time_agent/`**: Specialized weather and time information agent
- **`engineering_knowledge_agent/`**: [db] Engineering knowledge specialist with Databricks integration
- **`general_chat_agent/`**: General conversation and advice agent
- **`requirements.txt`**: Python dependencies
- **`.env`**: Environment configuration (includes Databricks credentials)

## Agent Transfer System

The system includes seamless agent-to-agent transfer capabilities:

- **Intelligent Routing**: Master coordinator automatically routes requests to appropriate specialists
- **Peer-to-Peer Transfers**: Individual agents can transfer conversations when queries fall outside their expertise
- **Context Preservation**: Transfers maintain conversation context and history

### Transfer Examples:
- Weather agent → Engineering Knowledge agent (for technical questions)
- Engineering Knowledge agent → Weather agent (for weather queries)
- Any agent → General Chat agent (for casual conversation)

## Databricks Integration

The Engineering Knowledge Agent [db] provides:

- **Service Principal Authentication**: Secure access using Azure AD service principal
- **RAG-Enabled Queries**: Leverages Databricks serving endpoints with engineering knowledge base
- **OpenAI-Compatible API**: Uses familiar OpenAI client interface with Databricks backend
- **Engineering Focus**: Specialized for technical documentation and engineering data queries

### Supported Model:
- `agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2`: Advanced RAG model for engineering queries

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

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Original Blog Post](https://michaelkabuage.com/blog/13-google-adk-azure)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
