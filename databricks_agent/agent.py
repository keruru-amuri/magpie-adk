import os
import requests
from typing import Dict, Any, Optional, List
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "azure/gpt-4.1")

# Get Databricks configuration from environment
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
ARM_TENANT_ID = os.getenv("ARM_TENANT_ID")
ARM_CLIENT_ID = os.getenv("ARM_CLIENT_ID")
ARM_CLIENT_SECRET = os.getenv("ARM_CLIENT_SECRET")

# Set LiteLLM environment variables for Azure OpenAI
# LiteLLM expects these specific variable names
os.environ["AZURE_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = AZURE_OPENAI_API_VERSION


class DatabricksClient:
    """Client for interacting with Databricks using service principal authentication."""
    
    def __init__(self):
        self.host = DATABRICKS_HOST
        self.tenant_id = ARM_TENANT_ID
        self.client_id = ARM_CLIENT_ID
        self.client_secret = ARM_CLIENT_SECRET
        self._access_token = None
    
    def _get_access_token(self) -> Optional[str]:
        """Get access token from Azure AD using service principal."""
        try:
            # Azure OAuth2 token endpoint
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
            
            # Request payload for client credentials flow
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default'  # Databricks scope
            }
            
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data.get('access_token')
            return self._access_token
            
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None
    
    def get_openai_client(self) -> Optional[OpenAI]:
        """Get OpenAI client configured for Databricks serving endpoints."""
        token = self._get_access_token()
        if not token:
            return None
        
        try:
            client = OpenAI(
                api_key=token,
                base_url=f"{self.host}/serving-endpoints"
            )
            return client
        except Exception as e:
            print(f"Error creating OpenAI client: {e}")
            return None


# Initialize Databricks client
databricks_client = DatabricksClient()


def query_databricks_llm(query: str, model_name: str = "agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2") -> Dict[str, Any]:
    """Query a Databricks LLM serving endpoint.
    
    Args:
        query: The question or prompt to send to the model
        model_name: The name of the Databricks model serving endpoint
        
    Returns:
        dict: Response from the Databricks model or error information
    """
    try:
        client = databricks_client.get_openai_client()
        if not client:
            return {
                "status": "error",
                "message": "Failed to authenticate with Databricks",
                "error": "Could not obtain access token"
            }
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        
        return {
            "status": "success",
            "response": response.choices[0].message.content,
            "model": model_name,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error querying Databricks model: {str(e)}",
            "model": model_name,
            "query": query
        }


def get_available_models() -> Dict[str, Any]:
    """Get information about available Databricks model serving endpoints.
    
    Returns:
        dict: Information about available models and endpoints
    """
    return {
        "status": "success",
        "available_models": [
            {
                "name": "agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2",
                "description": "Advanced RAG model for engineering data queries",
                "type": "LLM with RAG capabilities",
                "use_cases": ["Engineering data questions", "Technical documentation queries", "Knowledge base search"]
            }
        ],
        "endpoint_base": f"{DATABRICKS_HOST}/serving-endpoints",
        "authentication": "Service Principal (Azure AD)",
        "note": "Models are hosted on Databricks and accessed via OpenAI-compatible API"
    }


def get_databricks_status() -> Dict[str, Any]:
    """Get the status of the Databricks connection and configuration.
    
    Returns:
        dict: Status information about the Databricks connection
    """
    try:
        # Test authentication
        token = databricks_client._get_access_token()
        auth_status = "success" if token else "failed"
        
        return {
            "status": "success",
            "databricks_host": DATABRICKS_HOST,
            "authentication_status": auth_status,
            "client_id": ARM_CLIENT_ID[:8] + "..." if ARM_CLIENT_ID else "Not configured",
            "tenant_id": ARM_TENANT_ID[:8] + "..." if ARM_TENANT_ID else "Not configured",
            "connection_type": "Service Principal Authentication",
            "api_compatibility": "OpenAI-compatible endpoints"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking Databricks status: {str(e)}",
            "databricks_host": DATABRICKS_HOST or "Not configured"
        }


def transfer_to_weather_agent(tool_context: ToolContext) -> Dict[str, Any]:
    """Transfer the conversation to the weather and time specialist agent.

    Args:
        tool_context: The tool context for handling the transfer

    Returns:
        dict: Transfer confirmation
    """
    try:
        tool_context.actions.transfer_to_agent = "weather_time_agent"
        return {
            "status": "success",
            "message": "Transferring to weather and time specialist agent for weather-related queries.",
            "transferred_to": "weather_time_agent"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to transfer to weather agent: {str(e)}"
        }


def transfer_to_general_chat_agent(tool_context: ToolContext) -> Dict[str, Any]:
    """Transfer the conversation to the general chat agent.

    Args:
        tool_context: The tool context for handling the transfer

    Returns:
        dict: Transfer confirmation
    """
    try:
        tool_context.actions.transfer_to_agent = "general_chat_agent"
        return {
            "status": "success",
            "message": "Transferring to general chat agent for broader conversations and non-technical queries.",
            "transferred_to": "general_chat_agent"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to transfer to general chat agent: {str(e)}"
        }


def get_agent_capabilities() -> Dict[str, Any]:
    """Returns information about this agent's capabilities.

    Returns:
        dict: Information about the agent's capabilities
    """
    return {
        "status": "success",
        "capabilities": [
            "Query Databricks LLM serving endpoints",
            "Access engineering RAG models for technical questions",
            "Authenticate using Azure service principal",
            "Provide information about available models",
            "Check Databricks connection status",
            "Handle technical and engineering-related queries",
            "Transfer to weather agent for weather-related queries",
            "Transfer to general chat agent for non-technical conversations"
        ],
        "description": (
            "I'm a Databricks agent that can query LLM models hosted on Databricks serving endpoints. "
            "I use service principal authentication to securely access Databricks resources and can "
            "help with engineering data queries, technical documentation questions, and knowledge base searches. "
            "I can also transfer conversations to other specialist agents when appropriate."
        ),
        "authentication": "Azure Service Principal",
        "supported_endpoints": "OpenAI-compatible Databricks serving endpoints",
        "transfer_capabilities": [
            "weather_time_agent: For weather reports and time information",
            "general_chat_agent: For general conversations and non-technical queries"
        ]
    }


# Create the Databricks agent
root_agent = LlmAgent(
    name="databricks_agent",
    model=LiteLlm(model=AZURE_OPENAI_MODEL),  # Using Azure OpenAI via LiteLLM for agent reasoning
    description=(
        "Specialized agent for querying Databricks LLM serving endpoints. "
        "Handles technical and engineering queries using RAG-enabled models hosted on Databricks. "
        "Uses service principal authentication for secure access to Databricks resources."
    ),
    instruction=(
        "You are a Databricks specialist agent with access to LLM models hosted on Databricks serving endpoints. "
        "Your primary role is to help users query and interact with Databricks-hosted AI models, particularly "
        "for engineering and technical questions. "
        "\n\n"
        "CAPABILITIES:\n"
        "- Query Databricks LLM serving endpoints using OpenAI-compatible API\n"
        "- Access RAG-enabled models for engineering data and technical documentation\n"
        "- Provide information about available models and their capabilities\n"
        "- Check Databricks connection status and troubleshoot issues\n"
        "\n\n"
        "USAGE GUIDELINES:\n"
        "- Use 'query_databricks_llm' to send questions to Databricks models\n"
        "- Use 'get_available_models' to show users what models are available\n"
        "- Use 'get_databricks_status' to check connection and authentication status\n"
        "- For engineering, technical, or data-related questions, leverage the RAG capabilities\n"
        "- Always provide clear explanations of model responses and any limitations\n"
        "\n\n"
        "TRANSFER CAPABILITIES:\n"
        "- If users ask about weather or time information, use 'transfer_to_weather_agent'\n"
        "- If users ask general questions unrelated to technical/engineering topics, use 'transfer_to_general_chat_agent'\n"
        "- Only transfer when the query is clearly outside your technical expertise\n"
        "\n\n"
        "When users ask technical or engineering questions, use the Databricks models to provide "
        "accurate, up-to-date information from the engineering knowledge base. "
        "Be helpful in explaining both the query process and the results. "
        "For non-technical queries, don't hesitate to transfer to the appropriate specialist agent."
    ),
    tools=[query_databricks_llm, get_available_models, get_databricks_status, get_agent_capabilities, transfer_to_weather_agent, transfer_to_general_chat_agent],
)
