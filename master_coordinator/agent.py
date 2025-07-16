import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Import model factory for multi-model support
from common.model_factory import create_model_for_agent

# Import sub-agents
from general_chat_agent.agent import root_agent as general_chat_agent
from engineering_process_procedure_agent.agent import root_agent as engineering_process_procedure_agent
from data_scientist_agent.agent import data_scientist_agent

# Load environment variables from .env file
load_dotenv()

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

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
        "system": "MAGPIE Platform for Intelligent Execution",
        "coordinator": "Master Coordinator Agent",
        "available_agents": [
            {
                "name": "general_chat_agent",
                "description": "Handles general conversations and non-specialized requests",
                "specialties": ["general chat", "advice", "motivation", "casual conversation"]
            },
            {
                "name": "engineering_process_procedure_agent",
                "description": "Engineering Process Procedure Agent - Two-stage pipeline for aviation MRO queries with automatic enhancement and Databricks processing",
                "specialties": ["aviation maintenance", "aircraft MRO", "engineering procedures", "regulatory compliance", "databricks queries", "sequential processing"]
            },
            {
                "name": "data_scientist_agent",
                "description": "Specialized agent for data science tasks using Databricks through centralized MCP infrastructure",
                "specialties": ["data analysis", "SQL queries", "business intelligence", "cluster management", "data exploration", "statistical analysis"]
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
            "general_chat_agent": [
                "General conversations",
                "Advice and motivation",
                "Creative writing help",
                "General knowledge questions",
                "Casual chat and discussion",
                "Non-specialized requests"
            ],
            "engineering_process_procedure_agent": [
                "Aircraft maintenance and MRO questions",
                "Aviation engineering procedures",
                "Regulatory compliance queries",
                "Technical documentation searches",
                "Aviation safety protocols",
                "Component maintenance procedures",
                "Databricks-powered aviation knowledge retrieval"
            ],
            "data_scientist_agent": [
                "Data analysis and exploration",
                "SQL queries and database operations",
                "Business intelligence and reporting",
                "Statistical analysis and insights",
                "Data quality assessment",
                "Cluster management and resource optimization",
                "Data science workflows and processing"
            ]
        },
        "note": "The coordinator automatically routes your request to the most appropriate specialist agent."
    }

# Create the master coordinator agent with sub-agents
root_agent = LlmAgent(
    name="master_coordinator",
    model=create_model_for_agent("master_coordinator"),  # Using GPT-4.1 for strong routing decisions
    description=(
        "Master coordinator agent that intelligently routes user requests to specialized sub-agents. "
        "Manages the MAGPIE platform with engineering process specialists and general conversation capabilities."
    ),
    instruction=(
        "You are the Master Coordinator for the MAGPIE Platform for Intelligent Execution. Your primary role is to "
        "analyze incoming user requests and route them to the most appropriate specialist agent. "
        "\n\n"
        "ROUTING GUIDELINES:\n"
        "- For aviation maintenance, aircraft MRO, engineering procedures, or technical questions: "
        "Use transfer_to_agent(agent_name='engineering_process_procedure_agent')\n"
        "- For data analysis, SQL queries, business intelligence, or data science tasks: "
        "Use transfer_to_agent(agent_name='data_scientist_agent')\n"
        "- For general conversation, advice, motivation, creative help, or non-specialized requests: "
        "Use transfer_to_agent(agent_name='general_chat_agent')\n"
        "\n\n"
        "AVAILABLE AGENTS:\n"
        "1. engineering_process_procedure_agent: Sequential Agent for aviation MRO and engineering questions with automatic query enhancement\n"
        "2. data_scientist_agent: Specialized agent for data science tasks using Databricks through centralized MCP infrastructure\n"
        "3. general_chat_agent: Handles general conversations, advice, and casual interactions\n"
        "\n\n"
        "Always analyze the user's request carefully and route to the most appropriate agent. "
        "If you're unsure, default to the general_chat_agent for broader conversations. "
        "You can also provide system information using your tools when asked about the system itself."
    ),
    tools=[get_system_status, get_routing_help],
    sub_agents=[engineering_process_procedure_agent, data_scientist_agent, general_chat_agent],  # This enables LLM-driven delegation
)
