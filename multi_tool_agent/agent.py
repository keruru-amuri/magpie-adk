import os
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
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

def get_agent_info() -> dict:
    """Returns information about this agent and its capabilities.
    
    Returns:
        dict: Information about the agent.
    """
    return {
        "status": "success",
        "report": (
            "I am a weather and time agent powered by Google ADK and Azure OpenAI. "
            f"I'm using the {AZURE_OPENAI_MODEL} model via LiteLLM. "
            "I can provide weather information and current time for major cities including "
            "New York, London, Tokyo, Los Angeles, Paris, and Sydney."
        )
    }

# Create the root agent following ADK documentation structure with LiteLLM
root_agent = LlmAgent(
    name="weather_time_agent",
    model=LiteLlm(model=AZURE_OPENAI_MODEL),  # Using Azure OpenAI via LiteLLM
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time, get_agent_info],
)
