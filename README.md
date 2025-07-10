# AMOS Multi-Agent System with Google ADK and Azure OpenAI

This project implements a sophisticated multi-agent system using Google Agent Development Kit (ADK) with Azure OpenAI models via LiteLLM. The system features a master coordinator that intelligently routes requests to specialized sub-agents.

## Features

- **Multi-Agent Architecture**: Master coordinator with specialized sub-agents
- **Google ADK Integration**: Uses Google's Agent Development Kit for agent orchestration
- **Azure OpenAI**: Leverages Azure OpenAI GPT-4.1 model via LiteLLM
- **Intelligent Routing**: LLM-driven delegation between specialized agents
- **Specialized Agents**: Weather/time specialist and general conversation agent
- **Web Interface**: Provides a web-based chat interface via `adk web`

## Prerequisites

- Python 3.8+
- Azure OpenAI account with GPT-4.1 deployment
- Valid Azure OpenAI API credentials

## Configuration

The project uses environment variables defined in `.env`:

```env
# Azure OpenAI API Configuration
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Model Configuration
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_MODEL=azure/gpt-4.1
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
┌─────────────────────────────────────────────────────────────┐
│                    AMOS Multi-Agent System                  │
├─────────────────────────────────────────────────────────────┤
│                   Master Coordinator                       │
│              (LLM-Driven Delegation)                       │
├─────────────────────┬───────────────────────────────────────┤
│  Weather Time Agent │         General Chat Agent          │
│  ┌─────────────────┐│  ┌─────────────────────────────────┐ │
│  │ • Weather Info  ││  │ • General Conversation         │ │
│  │ • Time Zones    ││  │ • Advice & Motivation          │ │
│  │ • City Support  ││  │ • Creative Help                │ │
│  └─────────────────┘│  │ • Casual Chat                  │ │
│                     │  └─────────────────────────────────┘ │
└─────────────────────┴───────────────────────────────────────┘
                              │
                    ┌──────────────┐    ┌─────────────────┐
                    │   LiteLLM    │───▶│  Azure OpenAI   │
                    │  (Proxy)     │    │   (GPT-4.1)     │
                    └──────────────┘    └─────────────────┘
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
- **`general_chat_agent/`**: General conversation and advice agent
- **`requirements.txt`**: Python dependencies
- **`.env`**: Environment configuration

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
