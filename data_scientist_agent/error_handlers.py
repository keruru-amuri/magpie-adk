"""
Error handling utilities for the data scientist agent.

This module provides robust error handling for common issues like JSON parsing errors,
malformed function arguments, and tool execution failures.
"""

import json
import logging
import re
from functools import wraps
from typing import Any, Dict, Callable

logger = logging.getLogger(__name__)


def safe_json_parse_tool_args(func: Callable) -> Callable:
    """
    Decorator to safely handle JSON parsing errors in tool function arguments.
    
    This addresses the common issue where LLMs generate malformed JSON in function calls,
    particularly when dealing with table descriptions containing special characters.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in {func.__name__}: {e}")
            
            # Try to provide helpful error message
            error_msg = f"Error parsing function arguments. This often happens when descriptions contain special characters like quotes or newlines. Please try rephrasing your request with simpler descriptions."
            
            return {
                "status": "error",
                "error": error_msg,
                "technical_details": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            return {
                "status": "error", 
                "error": f"An unexpected error occurred: {str(e)}"
            }
    
    return wrapper


def sanitize_description_text(text: str) -> str:
    """
    Sanitize text descriptions to prevent JSON parsing issues.
    
    Args:
        text: Raw description text that may contain problematic characters
        
    Returns:
        Sanitized text safe for JSON serialization
    """
    if not text:
        return ""
    
    # Remove or replace problematic characters
    text = text.replace('\x00', '')  # Remove null bytes
    text = text.replace('\b', '')    # Remove backspace
    text = text.replace('\f', '')    # Remove form feed
    text = text.replace('\v', '')    # Remove vertical tab
    text = text.replace('\r\n', ' ') # Replace Windows line endings
    text = text.replace('\n', ' ')   # Replace line feeds
    text = text.replace('\r', ' ')   # Replace carriage returns
    text = text.replace('\t', ' ')   # Replace tabs
    
    # Escape quotes properly
    text = text.replace('"', '\\"')  # Escape double quotes
    text = text.replace("'", "\\'")  # Escape single quotes
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Limit length to prevent issues
    if len(text) > 1000:
        text = text[:997] + "..."
        logger.warning("Truncated description text to 1000 characters")
    
    return text


def validate_table_context_data(context_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize table context data before processing.
    
    Args:
        context_data: Raw context data from user input
        
    Returns:
        Sanitized and validated context data
    """
    if not isinstance(context_data, dict):
        logger.error("Context data must be a dictionary")
        return {}
    
    sanitized = {}
    
    # Sanitize business context
    if "business_context" in context_data:
        business_context = context_data["business_context"]
        if isinstance(business_context, dict):
            sanitized["business_context"] = {
                k: sanitize_description_text(str(v)) if isinstance(v, str) else v
                for k, v in business_context.items()
            }
        else:
            sanitized["business_context"] = {}
    
    # Sanitize field mappings
    if "field_mappings" in context_data:
        field_mappings = context_data["field_mappings"]
        if isinstance(field_mappings, dict):
            sanitized_mappings = {}
            for field_name, field_info in field_mappings.items():
                if isinstance(field_info, dict):
                    sanitized_field_info = {}
                    for key, value in field_info.items():
                        if isinstance(value, str):
                            sanitized_field_info[key] = sanitize_description_text(value)
                        else:
                            sanitized_field_info[key] = value
                    sanitized_mappings[field_name] = sanitized_field_info
                else:
                    sanitized_mappings[field_name] = field_info
            sanitized["field_mappings"] = sanitized_mappings
        else:
            sanitized["field_mappings"] = {}
    
    # Sanitize transformations
    if "transformations" in context_data:
        transformations = context_data["transformations"]
        if isinstance(transformations, dict):
            sanitized["transformations"] = {
                k: {
                    sub_k: sanitize_description_text(str(sub_v)) if isinstance(sub_v, str) else sub_v
                    for sub_k, sub_v in v.items()
                } if isinstance(v, dict) else v
                for k, v in transformations.items()
            }
        else:
            sanitized["transformations"] = {}
    
    # Sanitize common queries
    if "common_queries" in context_data:
        common_queries = context_data["common_queries"]
        if isinstance(common_queries, list):
            sanitized["common_queries"] = [
                sanitize_description_text(str(query)) if isinstance(query, str) else query
                for query in common_queries
            ]
        else:
            sanitized["common_queries"] = []
    
    return sanitized


def create_user_friendly_error_message(error: Exception) -> str:
    """
    Create user-friendly error messages for common issues.
    
    Args:
        error: The exception that occurred
        
    Returns:
        User-friendly error message with suggestions
    """
    error_str = str(error).lower()
    
    if "unterminated string" in error_str or "json" in error_str:
        return (
            "There was an issue processing your request due to special characters in the descriptions. "
            "Please try using simpler descriptions without quotes, newlines, or special characters. "
            "For example, instead of 'Customer's \"primary\" address', use 'Customer primary address'."
        )
    
    elif "column" in error_str and "comment" in error_str:
        return (
            "There was an issue setting column descriptions. This might be due to special characters "
            "or very long descriptions. Please try using shorter, simpler descriptions for your columns."
        )
    
    elif "table" in error_str and "not found" in error_str:
        return (
            "The specified table was not found. Please check the table name and ensure it exists "
            "in your Databricks workspace."
        )
    
    else:
        return f"An error occurred: {str(error)}. Please try rephrasing your request or contact support if the issue persists."


# Export the main functions
__all__ = [
    'safe_json_parse_tool_args',
    'sanitize_description_text', 
    'validate_table_context_data',
    'create_user_friendly_error_message'
]
