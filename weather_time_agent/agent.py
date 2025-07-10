import os
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext
from dotenv import load_dotenv

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

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the weather report.
    
    Returns:
        dict: status and result or error msg.
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    elif city.lower() == "london":
        return {
            "status": "success", 
            "report": (
                "The weather in London is cloudy with a temperature of 15 degrees"
                " Celsius (59 degrees Fahrenheit)."
            ),
        }
    elif city.lower() == "tokyo":
        return {
            "status": "success",
            "report": (
                "The weather in Tokyo is partly cloudy with a temperature of 22 degrees"
                " Celsius (72 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the current time.
    
    Returns:
        dict: status and result or error msg.
    """
    
    city_timezones = {
        "new york": "America/New_York",
        "london": "Europe/London", 
        "tokyo": "Asia/Tokyo",
        "los angeles": "America/Los_Angeles",
        "paris": "Europe/Paris",
        "sydney": "Australia/Sydney"
    }
    
    city_lower = city.lower()
    if city_lower in city_timezones:
        tz_identifier = city_timezones[city_lower]
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }
    
    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

def get_supported_cities() -> dict:
    """Returns a list of cities supported by this agent.

    Returns:
        dict: List of supported cities.
    """
    return {
        "status": "success",
        "supported_cities": [
            "New York", "London", "Tokyo", "Los Angeles", "Paris", "Sydney"
        ],
        "message": "I can provide weather and time information for these major cities."
    }


def transfer_to_engineering_knowledge_agent(tool_context: ToolContext) -> dict:
    """Transfer the conversation to the Engineering Knowledge Agent [db].

    Args:
        tool_context: The tool context for handling the transfer

    Returns:
        dict: Transfer confirmation
    """
    try:
        tool_context.actions.transfer_to_agent = "engineering_knowledge_agent_db"
        return {
            "status": "success",
            "message": "Transferring to Engineering Knowledge Agent [db] for technical and engineering queries.",
            "transferred_to": "engineering_knowledge_agent_db"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to transfer to Engineering Knowledge Agent: {str(e)}"
        }


def transfer_to_general_chat_agent(tool_context: ToolContext) -> dict:
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
            "message": "Transferring to general chat agent for broader conversations and non-weather topics.",
            "transferred_to": "general_chat_agent"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to transfer to general chat agent: {str(e)}"
        }

# Create the weather and time specialist agent
root_agent = LlmAgent(
    name="weather_time_agent",
    model=LiteLlm(model=AZURE_OPENAI_MODEL),  # Using Azure OpenAI via LiteLLM
    description=(
        "Specialized agent for weather reports and current time information in major cities. "
        "Handles all weather-related queries and time zone information for supported cities."
    ),
    instruction=(
        "You are a specialized weather and time information agent. "
        "Your primary role is to provide accurate weather reports and current time information "
        "for major cities around the world. "
        "You support New York, London, Tokyo, Los Angeles, Paris, and Sydney. "
        "Always use the appropriate tools to get weather or time information when requested. "
        "\n\n"
        "TRANSFER CAPABILITIES:\n"
        "- If users ask technical or engineering questions, use 'transfer_to_engineering_knowledge_agent'\n"
        "- If users ask general questions unrelated to weather/time, use 'transfer_to_general_chat_agent'\n"
        "- Only transfer when the query is clearly outside your weather and time expertise\n"
        "\n\n"
        "For weather and time queries, handle them directly using your tools. "
        "For other topics, transfer to the appropriate specialist agent."
    ),
    tools=[get_weather, get_current_time, get_supported_cities, transfer_to_engineering_knowledge_agent, transfer_to_general_chat_agent],
)
