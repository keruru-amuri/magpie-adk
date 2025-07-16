"""
Model Factory for MAGPIE Platform Multi-Model Support

This module provides a centralized factory for creating model instances
based on agent type and configuration strategy.
"""

import os
from typing import Optional, Dict, Any
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelFactory:
    """Factory class for creating model instances based on configuration."""
    
    # Agent type to environment variable mapping
    AGENT_MODEL_MAPPING = {
        'master_coordinator': 'MASTER_COORDINATOR_MODEL',
        'engineering_process_procedure_agent': 'ENGINEERING_PROCESS_AGENT_MODEL',
        'general_chat_agent': 'GENERAL_CHAT_AGENT_MODEL',
        'data_scientist_agent': 'DATA_SCIENTIST_AGENT_MODEL',
        'query_enhancement_agent': 'QUERY_ENHANCEMENT_AGENT_MODEL',
        'databricks_query_agent': 'DATABRICKS_QUERY_AGENT_MODEL',
        # Aliases for backward compatibility
        'QueryEnhancementAgent': 'QUERY_ENHANCEMENT_AGENT_MODEL',
        'DatabricksQueryAgent': 'DATABRICKS_QUERY_AGENT_MODEL',
    }
    
    # Available models configuration
    AVAILABLE_MODELS = {
        'gpt-4.1': 'AVAILABLE_MODELS_GPT41',
        'gpt-4.1-mini': 'AVAILABLE_MODELS_GPT41_MINI',
        'gpt-4.1-nano': 'AVAILABLE_MODELS_GPT41_NANO',
        'deepseek': 'AVAILABLE_MODELS_DEEPSEEK',
    }
    
    @classmethod
    def create_model(cls, agent_name: str, **kwargs) -> LiteLlm:
        """
        Create a model instance for the specified agent.
        
        Args:
            agent_name: Name of the agent requesting the model
            **kwargs: Additional parameters for model configuration
            
        Returns:
            LiteLlm: Configured model instance
        """
        model_string = cls._get_model_for_agent(agent_name)
        
        # Create LiteLlm instance with the determined model
        model_instance = LiteLlm(model=model_string, **kwargs)
        
        # Log model selection for debugging
        if os.getenv('AGENT_LOG_LEVEL', 'INFO') in ['DEBUG', 'INFO']:
            print(f"🤖 Agent '{agent_name}' using model: {model_string}")
        
        return model_instance
    
    @classmethod
    def _get_model_for_agent(cls, agent_name: str) -> str:
        """
        Determine which model to use for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            str: Model string in azure/model-name format
        """
        strategy = os.getenv('MODEL_SELECTION_STRATEGY', 'agent_specific')
        
        if strategy == 'agent_specific':
            return cls._get_agent_specific_model(agent_name)
        elif strategy == 'default':
            return cls._get_default_model()
        elif strategy == 'environment':
            return cls._get_environment_model()
        else:
            print(f"⚠️  Unknown model selection strategy: {strategy}. Using default.")
            return cls._get_default_model()
    
    @classmethod
    def _get_agent_specific_model(cls, agent_name: str) -> str:
        """Get agent-specific model configuration."""
        # Normalize agent name for lookup
        normalized_name = agent_name.lower().replace('-', '_')
        
        # Try direct mapping first
        env_var = cls.AGENT_MODEL_MAPPING.get(normalized_name)
        
        # If not found, try partial matching
        if not env_var:
            for key, var in cls.AGENT_MODEL_MAPPING.items():
                if key in normalized_name or normalized_name in key:
                    env_var = var
                    break
        
        if env_var:
            model = os.getenv(env_var)
            if model:
                return model
            else:
                print(f"⚠️  Agent-specific model not configured for {agent_name} ({env_var}). Using default.")
        else:
            print(f"⚠️  No model mapping found for agent: {agent_name}. Using default.")
        
        # Fallback to default
        return cls._get_default_model()
    
    @classmethod
    def _get_default_model(cls) -> str:
        """Get the default model configuration."""
        default_model = os.getenv('DEFAULT_LLM_MODEL')
        if default_model:
            return default_model
        
        # Fallback to environment model
        return cls._get_environment_model()
    
    @classmethod
    def _get_environment_model(cls) -> str:
        """Get the legacy environment model configuration."""
        env_model = os.getenv('AZURE_OPENAI_MODEL', 'azure/gpt-4.1')
        return env_model
    
    @classmethod
    def get_available_models(cls) -> Dict[str, str]:
        """
        Get all available models and their configurations.
        
        Returns:
            Dict[str, str]: Mapping of model names to their configurations
        """
        models = {}
        for model_name, env_var in cls.AVAILABLE_MODELS.items():
            model_config = os.getenv(env_var)
            if model_config:
                models[model_name] = model_config
        return models
    
    @classmethod
    def validate_configuration(cls) -> Dict[str, Any]:
        """
        Validate the current model configuration.
        
        Returns:
            Dict[str, Any]: Validation results
        """
        results = {
            'strategy': os.getenv('MODEL_SELECTION_STRATEGY', 'agent_specific'),
            'available_models': cls.get_available_models(),
            'agent_configurations': {},
            'issues': []
        }
        
        # Check agent configurations
        for agent_name, env_var in cls.AGENT_MODEL_MAPPING.items():
            model_config = os.getenv(env_var)
            results['agent_configurations'][agent_name] = model_config
            
            if not model_config and results['strategy'] == 'agent_specific':
                results['issues'].append(f"Missing configuration for {agent_name} ({env_var})")
        
        # Check default fallbacks
        if not os.getenv('DEFAULT_LLM_MODEL'):
            results['issues'].append("DEFAULT_LLM_MODEL not configured")
        
        if not os.getenv('AZURE_OPENAI_MODEL'):
            results['issues'].append("AZURE_OPENAI_MODEL not configured")
        
        return results
    
    @classmethod
    def get_model_info(cls, agent_name: str) -> Dict[str, str]:
        """
        Get information about which model an agent would use.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dict[str, str]: Model information
        """
        model_string = cls._get_model_for_agent(agent_name)
        strategy = os.getenv('MODEL_SELECTION_STRATEGY', 'agent_specific')
        
        return {
            'agent_name': agent_name,
            'model': model_string,
            'strategy': strategy,
            'source': cls._get_model_source(agent_name, strategy)
        }
    
    @classmethod
    def _get_model_source(cls, agent_name: str, strategy: str) -> str:
        """Get the source of the model configuration."""
        if strategy == 'agent_specific':
            normalized_name = agent_name.lower().replace('-', '_')
            env_var = cls.AGENT_MODEL_MAPPING.get(normalized_name)
            if env_var and os.getenv(env_var):
                return f"Agent-specific ({env_var})"
            else:
                return "Default fallback"
        elif strategy == 'default':
            return "DEFAULT_LLM_MODEL"
        elif strategy == 'environment':
            return "AZURE_OPENAI_MODEL"
        else:
            return "Unknown"


# Convenience function for creating models
def create_model_for_agent(agent_name: str, **kwargs) -> LiteLlm:
    """
    Convenience function to create a model for an agent.
    
    Args:
        agent_name: Name of the agent
        **kwargs: Additional model parameters
        
    Returns:
        LiteLlm: Configured model instance
    """
    return ModelFactory.create_model(agent_name, **kwargs)
