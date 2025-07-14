import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Import model factory for multi-model support
from common.model_factory import create_model_for_agent

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

def get_conversation_tips() -> dict:
    """Provides tips for having engaging conversations.
    
    Returns:
        dict: Conversation tips and suggestions.
    """
    return {
        "status": "success",
        "tips": [
            "Ask open-ended questions to encourage detailed responses",
            "Show genuine interest in the other person's experiences",
            "Share relevant personal stories to build connection",
            "Practice active listening and ask follow-up questions",
            "Find common interests and experiences to discuss"
        ]
    }

def get_daily_motivation() -> dict:
    """Provides daily motivational quotes and encouragement.
    
    Returns:
        dict: Motivational content.
    """
    motivational_quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "Your limitation—it's only your imagination.",
        "Push yourself, because no one else is going to do it for you.",
        "Great things never come from comfort zones.",
        "Dream it. Wish it. Do it.",
        "Success doesn't just find you. You have to go out and get it.",
        "The harder you work for something, the greater you'll feel when you achieve it."
    ]
    
    import random
    selected_quote = random.choice(motivational_quotes)
    
    return {
        "status": "success",
        "quote": selected_quote,
        "message": "Remember, every day is a new opportunity to grow and achieve your goals!"
    }

def transfer_to_engineering_process_procedure_agent() -> dict:
    """Transfer the conversation to the Engineering Process Procedure Agent for technical queries.

    Returns:
        dict: Transfer confirmation
    """
    return {
        "status": "transfer_initiated",
        "target_agent": "engineering_process_procedure_agent",
        "message": "I'll transfer you to the Engineering Process Procedure Agent who specializes in technical and aviation engineering queries."
    }


def get_agent_capabilities() -> dict:
    """Returns information about this agent's capabilities.

    Returns:
        dict: Information about the agent's capabilities.
    """
    return {
        "status": "success",
        "capabilities": [
            "Engaging in general conversations on various topics",
            "Providing motivational quotes and encouragement",
            "Offering conversation tips and social advice",
            "Discussing current events, hobbies, and interests",
            "Helping with creative writing and brainstorming",
            "Providing general knowledge and explanations",
            "Transfer to Engineering Process Procedure agent for technical/engineering questions"
        ],
        "description": (
            "I'm a general conversation agent powered by Azure OpenAI GPT-4.1 via LiteLLM. "
            "I'm designed to have natural, engaging conversations on a wide variety of topics. "
            "I can help with general questions, provide motivation, offer advice, and simply chat! "
            "I can also transfer conversations to specialist agents when needed."
        ),
        "transfer_capabilities": [
            "engineering_process_procedure_agent: For technical and engineering questions"
        ]
    }

# Create the general chat agent
root_agent = LlmAgent(
    name="general_chat_agent",
    model=create_model_for_agent("general_chat_agent"),  # Using GPT-4.1-mini for cost-effective conversation
    description=(
        "Handles general conversational interactions, provides motivation, "
        "offers advice, and engages in friendly chat on various topics. "
        "Perfect for general questions, casual conversation, and non-specialized requests."
    ),
    instruction=(
        "You are a friendly, helpful, and engaging conversational AI assistant. "
        "Your role is to have natural conversations with users on a wide variety of topics. "
        "You should be warm, supportive, and encouraging in your responses. "
        "You can discuss current events, hobbies, provide general advice, help with creative tasks, "
        "and simply chat about whatever the user is interested in. "
        "\n\n"
        "TRANSFER CAPABILITIES:\n"
        "- If users ask technical or engineering questions, use 'transfer_to_engineering_process_procedure_agent'\n"
        "- This will transfer to the Engineering Process Procedure Agent for aviation and technical queries\n"
        "- Only transfer when the query is clearly outside your general conversation expertise\n"
        "\n\n"
        "Always aim to be helpful, informative, and maintain a positive, friendly tone. "
        "For specialized topics, don't hesitate to transfer to the appropriate expert agent."
    ),
    tools=[get_conversation_tips, get_daily_motivation, get_agent_capabilities, transfer_to_engineering_process_procedure_agent],
)
