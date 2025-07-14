import os
import requests
from typing import Dict, Any
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Import model factory for multi-model support
from common.model_factory import create_model_for_agent

# Load environment variables
load_dotenv()

# Get Azure OpenAI configuration from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Set LiteLLM environment variables for Azure OpenAI
os.environ["AZURE_API_KEY"] = AZURE_OPENAI_API_KEY
os.environ["AZURE_API_BASE"] = AZURE_OPENAI_ENDPOINT
os.environ["AZURE_API_VERSION"] = AZURE_OPENAI_API_VERSION


class DatabricksClient:
    """Client for authenticating and communicating with Databricks."""
    
    def __init__(self):
        # Use the actual environment variable names from .env file
        self.workspace_url = os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_WORKSPACE_URL")
        self.client_id = os.getenv("ARM_CLIENT_ID") or os.getenv("DATABRICKS_CLIENT_ID")
        self.client_secret = os.getenv("ARM_CLIENT_SECRET") or os.getenv("DATABRICKS_CLIENT_SECRET")
        self.tenant_id = os.getenv("ARM_TENANT_ID") or os.getenv("DATABRICKS_TENANT_ID")
        self._access_token = None

    def _get_access_token(self) -> str:
        """Get access token using service principal authentication."""
        if self._access_token:
            return self._access_token

        # Validate required credentials
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            missing = []
            if not self.tenant_id: missing.append("ARM_TENANT_ID")
            if not self.client_id: missing.append("ARM_CLIENT_ID")
            if not self.client_secret: missing.append("ARM_CLIENT_SECRET")
            raise Exception(f"Missing required Databricks credentials: {', '.join(missing)}")

        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': '2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default'  # Databricks scope
        }

        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data['access_token']
            return self._access_token
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception(f"Authentication failed: Invalid client credentials. Please verify ARM_CLIENT_ID and ARM_CLIENT_SECRET in .env file")
            elif response.status_code == 400:
                error_details = response.json() if response.content else {}
                raise Exception(f"Bad request to Azure AD: {error_details.get('error_description', str(e))}")
            else:
                raise Exception(f"HTTP error {response.status_code}: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to get access token: {str(e)}")

    def get_openai_client(self):
        """Get OpenAI-compatible client for Databricks."""
        try:
            from openai import OpenAI

            # Validate workspace URL
            if not self.workspace_url:
                raise Exception("Missing DATABRICKS_HOST in .env file")

            access_token = self._get_access_token()

            client = OpenAI(
                api_key=access_token,
                base_url=f"{self.workspace_url}/serving-endpoints"
            )

            return client
        except Exception as e:
            print(f"Error creating Databricks client: {str(e)}")
            return None


# Global client instance
databricks_client = DatabricksClient()


def query_databricks_llm(enhanced_query: str, model_name: str = "agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2") -> Dict[str, Any]:
    """Query a Databricks LLM serving endpoint with the enhanced query.

    Args:
        enhanced_query: The aviation-enhanced query from the previous agent
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

        # Query the Databricks model
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": enhanced_query
                }
            ],
            max_tokens=2000,
            temperature=0.1
        )

        # Return the response
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
            "message": f"Error querying Databricks: {str(e)}",
            "error": str(e)
        }


def get_available_models() -> Dict[str, Any]:
    """Get information about available Databricks models.
    
    Returns:
        dict: Information about available models
    """
    return {
        "status": "success",
        "available_models": [
            {
                "name": "agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2",
                "description": "Advanced RAG model for engineering process and procedure queries",
                "type": "RAG-enabled LLM",
                "specialization": "Aircraft MRO and engineering documentation"
            }
        ],
        "default_model": "agents_engineering-demo_rag_mabes-rag_mabes_advanced_v8_2"
    }


def get_databricks_status() -> Dict[str, Any]:
    """Check the status of Databricks connection and authentication.

    Returns:
        dict: Status information about Databricks connectivity
    """
    try:
        # Check if credentials are available
        credentials_status = {
            "workspace_url": bool(databricks_client.workspace_url),
            "client_id": bool(databricks_client.client_id),
            "client_secret": bool(databricks_client.client_secret),
            "tenant_id": bool(databricks_client.tenant_id)
        }

        missing_creds = [k for k, v in credentials_status.items() if not v]

        if missing_creds:
            return {
                "status": "error",
                "message": f"Missing credentials: {', '.join(missing_creds)}",
                "connection_status": "Configuration Error",
                "credentials_status": credentials_status,
                "workspace_url": databricks_client.workspace_url
            }

        # Try to get access token
        try:
            access_token = databricks_client._get_access_token()
            token_available = bool(access_token)
        except Exception as token_error:
            return {
                "status": "error",
                "message": f"Authentication failed: {str(token_error)}",
                "connection_status": "Authentication Error",
                "credentials_status": credentials_status,
                "workspace_url": databricks_client.workspace_url
            }

        # Try to create client
        client = databricks_client.get_openai_client()
        if client:
            return {
                "status": "success",
                "message": "Successfully connected to Databricks",
                "workspace_url": databricks_client.workspace_url,
                "authentication": "Service Principal (Azure AD)",
                "connection_status": "Active",
                "credentials_status": credentials_status,
                "token_available": token_available
            }
        else:
            return {
                "status": "error",
                "message": "Failed to create Databricks client",
                "connection_status": "Client Creation Failed",
                "credentials_status": credentials_status,
                "workspace_url": databricks_client.workspace_url
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking Databricks status: {str(e)}",
            "connection_status": "Error"
        }


# Create the Databricks Query Agent
databricks_query_agent = LlmAgent(
    name="DatabricksQueryAgent",
    model=create_model_for_agent("databricks_query_agent"),  # Using GPT-4.1 for technical query processing
    description=(
        "Specialized agent that processes aviation-enhanced queries and interfaces with Databricks LLM endpoints. "
        "Takes enhanced queries from the Query Enhancement Agent and retrieves contextually accurate responses "
        "from the aviation knowledge base hosted on Databricks."
    ),
    instruction=(
        "You are a Databricks Query Agent specialized in processing aviation-enhanced queries. "
        "You receive enhanced queries with aviation context from the previous agent and use them to "
        "query Databricks LLM serving endpoints for accurate, contextually-rich responses. "
        "\n\n"
        "QUERY PROCESSING:\n"
        "1. Receive the enhanced query from the previous agent via state: {enhanced_query}\n"
        "2. Use the query_databricks_llm tool to send the enhanced query to Databricks\n"
        "3. Return the response from Databricks to the user\n"
        "\n\n"
        "AVAILABLE TOOLS:\n"
        "- query_databricks_llm: Send enhanced queries to Databricks LLM endpoints\n"
        "- get_available_models: Get information about available Databricks models\n"
        "- get_databricks_status: Check Databricks connection status\n"
        "\n\n"
        "The enhanced query contains aviation-specific context and terminology that will improve "
        "the quality and relevance of responses from the aviation knowledge base."
    ),
    tools=[query_databricks_llm, get_available_models, get_databricks_status],
    output_key="final_response"  # This stores the final response
)
