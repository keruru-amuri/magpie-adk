import os
from google.adk.agents import SequentialAgent
from dotenv import load_dotenv

# Import the sub-agents (they handle their own model configuration)
from .sub_agents.query_enhancement_agent.agent import query_enhancement_agent
from .sub_agents.databricks_query_agent.agent import databricks_query_agent

# Load environment variables
load_dotenv()

# Get Azure OpenAI configuration from environment for sub-agents
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Set LiteLLM environment variables for Azure OpenAI (used by sub-agents)
os.environ["AZURE_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = AZURE_OPENAI_API_VERSION


def get_agent_capabilities() -> dict:
    """Returns information about the Sequential Agent's capabilities.
    
    Returns:
        dict: Information about the agent's capabilities
    """
    return {
        "status": "success",
        "agent_type": "Sequential Agent",
        "architecture": "Two-stage pipeline with specialized sub-agents",
        "capabilities": [
            "Automatic aviation query enhancement with MRO terminology and regulatory context",
            "Transparent query processing - users receive enhanced responses without seeing enhancement",
            "Sequential workflow: Query Enhancement → Databricks Processing → Final Response",
            "Aviation domain expertise including maintenance, troubleshooting, regulatory, and safety contexts",
            "Integration with Databricks LLM serving endpoints for RAG-enabled responses",
            "Service principal authentication for secure Databricks access"
        ],
        "sub_agents": [
            {
                "name": "QueryEnhancementAgent",
                "purpose": "Transform user queries with aviation engineering and MRO-specific context",
                "input": "Raw user query (e.g., 'process of component robbing')",
                "output": "Enhanced query with aviation terminology, regulatory references, and best practices",
                "function": "Acts as preprocessing layer that enriches queries with domain expertise"
            },
            {
                "name": "DatabricksQueryAgent", 
                "purpose": "Process enhanced query and interface with Databricks LLM endpoint",
                "input": "Enhanced query from QueryEnhancementAgent",
                "output": "Contextually accurate response from aviation knowledge base",
                "function": "Handles Databricks communication and response formatting"
            }
        ],
        "workflow": "User Query → Query Enhancement → Enhanced Query → Databricks Processing → Final Response",
        "transparency": "Enhancement happens seamlessly in background - users receive better responses without complexity",
        "description": (
            "I'm an Engineering Process Procedure Agent specialized in aircraft MRO (Maintenance, Repair, and Overhaul) "
            "and aviation engineering. I use a two-stage pipeline to automatically enhance user queries with "
            "aviation-specific context before querying Databricks LLM endpoints. This ensures users receive "
            "more accurate and contextually relevant responses for aviation maintenance questions."
        )
    }


def transfer_to_general_chat_agent() -> dict:
    """Transfer control to the general chat agent for non-technical conversations.
    
    Returns:
        dict: Transfer confirmation
    """
    return {
        "status": "transfer_initiated",
        "target_agent": "general_chat_agent",
        "message": "Transferring to general chat agent for non-technical conversation."
    }


# Create the Sequential Agent that orchestrates the two sub-agents
root_agent = SequentialAgent(
    name="engineering_process_procedure_agent",
    sub_agents=[query_enhancement_agent, databricks_query_agent],  # Executed in this order
    description=(
        "Sequential Agent for aircraft MRO and aviation engineering queries. "
        "Implements a two-stage pipeline: (1) Query Enhancement with aviation context, "
        "(2) Databricks processing for contextually accurate responses. "
        "Provides transparent enhancement - users receive better responses without seeing the enhancement process."
    ),
    # Note: SequentialAgent doesn't use instruction, model, or tools directly
    # The workflow is handled by the sub-agents in sequence
)
