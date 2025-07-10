import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Import sub-agents
from weather_time_agent.agent import root_agent as weather_time_agent
from general_chat_agent.agent import root_agent as general_chat_agent

# Load environment variables from .env file
load_dotenv()

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "azure/gpt-4.1")

# Set LiteLLM environment variables for Azure OpenAI
# LiteLLM expects these specific variable names
os.environ["AZURE_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = AZURE_OPENAI_API_VERSION

def get_system_status() -> dict:
    """Returns the status of the multi-agent system.
    
    Returns:
        dict: System status and available agents.
    """
    return {
        "status": "success",
        "system": "AMOS Multi-Agent System",
        "coordinator": "Master Coordinator Agent",
        "available_agents": [
            {
                "name": "weather_time_agent",
                "description": "Handles weather reports and time information for major cities",
                "specialties": ["weather", "time", "timezone information"]
            },
            {
                "name": "general_chat_agent", 
                "description": "Handles general conversations and non-specialized requests",
                "specialties": ["general chat", "advice", "motivation", "casual conversation"]
            }
        ],
        "model": AZURE_OPENAI_MODEL,
        "powered_by": "Azure OpenAI via LiteLLM"
    }

def get_routing_help() -> dict:
    """Provides information about how requests are routed to appropriate agents.
    
    Returns:
        dict: Routing information and guidelines.
    """
    return {
        "status": "success",
        "routing_info": {
            "weather_time_agent": [
                "Weather reports for cities",
                "Current time in different cities", 
                "Timezone information",
                "Questions about weather conditions",
                "Time-related queries"
            ],
            "general_chat_agent": [
                "General conversations",
                "Advice and motivation",
                "Creative writing help",
                "General knowledge questions",
                "Casual chat and discussion",
                "Non-specialized requests"
            ]
        },
        "note": "The coordinator automatically routes your request to the most appropriate specialist agent."
    }

# Create the master coordinator agent with sub-agents
root_agent = LlmAgent(
    name="master_coordinator",
    model=LiteLlm(model=AZURE_OPENAI_MODEL),  # Using Azure OpenAI via LiteLLM
    description=(
        "Master coordinator agent that intelligently routes user requests to specialized sub-agents. "
        "Manages a multi-agent system with weather/time specialists and general conversation capabilities."
    ),
    instruction=(
        "You are the Master Coordinator for the AMOS Multi-Agent System. Your primary role is to "
        "analyze incoming user requests and route them to the most appropriate specialist agent. "
        "\n\n"
        "ROUTING GUIDELINES:\n"
        "- For weather reports, weather conditions, or current time in cities: "
        "Use transfer_to_agent(agent_name='weather_time_agent')\n"
        "- For general conversation, advice, motivation, creative help, or non-specialized requests: "
        "Use transfer_to_agent(agent_name='general_chat_agent')\n"
        "\n\n"
        "AVAILABLE AGENTS:\n"
        "1. weather_time_agent: Specialized in weather reports and time information for major cities\n"
        "2. general_chat_agent: Handles general conversations, advice, and casual interactions\n"
        "\n\n"
        "Always analyze the user's request carefully and route to the most appropriate agent. "
        "If you're unsure, default to the general_chat_agent for broader conversations. "
        "You can also provide system information using your tools when asked about the system itself."
    ),
    tools=[get_system_status, get_routing_help],
    sub_agents=[weather_time_agent, general_chat_agent],  # This enables LLM-driven delegation
)
