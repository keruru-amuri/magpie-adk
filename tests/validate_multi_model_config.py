#!/usr/bin/env python3
"""
Validation script for multi-model configuration.
Checks that all model configurations are properly set and accessible.
"""

import os
from dotenv import load_dotenv

def validate_multi_model_config():
    """Validate the multi-model configuration in .env file"""
    print("🔍 Validating Multi-Model Configuration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check basic Azure configuration
    azure_config = {
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION')
    }
    
    print("📋 Basic Azure Configuration:")
    for key, value in azure_config.items():
        if value:
            display_value = f"{'*' * 20}{value[-4:]}" if 'KEY' in key and len(value) > 4 else value
            print(f"  ✅ {key}: {display_value}")
        else:
            print(f"  ❌ {key}: Not set")
    
    # Check available models configuration
    available_models = {
        'GPT-4.1': os.getenv('AVAILABLE_MODELS_GPT41'),
        'GPT-4.1 Mini': os.getenv('AVAILABLE_MODELS_GPT41_MINI'),
        'GPT-4.1 Nano': os.getenv('AVAILABLE_MODELS_GPT41_NANO'),
        'DeepSeek-R1-0528': os.getenv('AVAILABLE_MODELS_DEEPSEEK')
    }
    
    print("\n📋 Available Models Configuration:")
    for model_name, model_config in available_models.items():
        if model_config:
            print(f"  ✅ {model_name}: {model_config}")
        else:
            print(f"  ❌ {model_name}: Not configured")
    
    # Check agent-specific configurations
    agent_models = {
        'Master Coordinator': os.getenv('MASTER_COORDINATOR_MODEL'),
        'Engineering Process Agent': os.getenv('ENGINEERING_PROCESS_AGENT_MODEL'),
        'Query Enhancement Agent': os.getenv('QUERY_ENHANCEMENT_AGENT_MODEL'),
        'Databricks Query Agent': os.getenv('DATABRICKS_QUERY_AGENT_MODEL'),
        'General Chat Agent': os.getenv('GENERAL_CHAT_AGENT_MODEL')
    }
    
    print("\n📋 Agent-Specific Model Configuration:")
    for agent_name, model_config in agent_models.items():
        if model_config:
            print(f"  ✅ {agent_name}: {model_config}")
        else:
            print(f"  ⚠️  {agent_name}: Not configured (will use default)")
    
    # Check model selection strategy
    strategy = os.getenv('MODEL_SELECTION_STRATEGY', 'default')
    print(f"\n📋 Model Selection Strategy: {strategy}")
    
    if strategy == 'agent_specific':
        print("  ✅ Using agent-specific model configurations")
    elif strategy == 'default':
        default_model = os.getenv('DEFAULT_LLM_MODEL')
        print(f"  ✅ Using default model for all agents: {default_model}")
    elif strategy == 'environment':
        env_model = os.getenv('AZURE_OPENAI_MODEL')
        print(f"  ✅ Using environment model for all agents: {env_model}")
    else:
        print(f"  ⚠️  Unknown strategy: {strategy}")
    
    # Check legacy configuration
    legacy_config = {
        'AZURE_OPENAI_MODEL': os.getenv('AZURE_OPENAI_MODEL'),
        'DEFAULT_LLM_MODEL': os.getenv('DEFAULT_LLM_MODEL')
    }
    
    print("\n📋 Legacy Configuration (Backward Compatibility):")
    for key, value in legacy_config.items():
        if value:
            print(f"  ✅ {key}: {value}")
        else:
            print(f"  ❌ {key}: Not set")
    
    # Validation summary
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    # Count configured items
    azure_configured = sum(1 for v in azure_config.values() if v)
    models_configured = sum(1 for v in available_models.values() if v)
    agents_configured = sum(1 for v in agent_models.values() if v)
    
    print(f"Azure Configuration: {azure_configured}/3 ({'✅' if azure_configured == 3 else '⚠️'})")
    print(f"Available Models: {models_configured}/4 ({'✅' if models_configured == 4 else '⚠️'})")
    print(f"Agent Configurations: {agents_configured}/5 ({'✅' if agents_configured >= 3 else '⚠️'})")
    
    # Overall status
    if azure_configured == 3 and models_configured >= 2:
        print("\n🎉 Configuration Status: READY")
        print("✅ Multi-model support is properly configured!")
    elif azure_configured == 3:
        print("\n⚠️  Configuration Status: PARTIAL")
        print("⚠️  Basic Azure config is ready, but model configurations need attention")
    else:
        print("\n❌ Configuration Status: INCOMPLETE")
        print("❌ Basic Azure configuration is missing")
    
    return azure_configured == 3 and models_configured >= 2

def test_model_access():
    """Test if we can access the configured models"""
    print("\n🧪 Testing Model Access")
    print("=" * 50)
    
    try:
        import litellm
        
        # Get Azure configuration
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        if not all([azure_api_key, azure_endpoint, azure_api_version]):
            print("❌ Cannot test - missing Azure configuration")
            return False
        
        # Set environment variables for LiteLLM
        os.environ["AZURE_API_KEY"] = azure_api_key
        os.environ["AZURE_API_BASE"] = azure_endpoint
        os.environ["AZURE_API_VERSION"] = azure_api_version
        
        # Test available models
        models_to_test = [
            ("GPT-4.1", os.getenv('AVAILABLE_MODELS_GPT41')),
            ("DeepSeek", os.getenv('AVAILABLE_MODELS_DEEPSEEK'))
        ]
        
        for model_name, model_config in models_to_test:
            if not model_config:
                print(f"⚠️  Skipping {model_name} - not configured")
                continue
                
            try:
                print(f"🔄 Testing {model_name} ({model_config})...")
                
                response = litellm.completion(
                    model=model_config,
                    messages=[{"role": "user", "content": "Hello! Just testing connectivity."}],
                    max_tokens=50,
                    api_key=azure_api_key,
                    api_base=azure_endpoint,
                    api_version=azure_api_version
                )
                
                print(f"✅ {model_name}: Connection successful")
                
            except Exception as e:
                print(f"❌ {model_name}: Connection failed - {str(e)}")
        
        return True
        
    except ImportError:
        print("⚠️  Cannot test model access - litellm not available")
        return False
    except Exception as e:
        print(f"❌ Model access test failed: {str(e)}")
        return False

def main():
    """Main validation function"""
    print("🚀 MAGPIE Multi-Model Configuration Validator")
    print("=" * 60)
    
    # Validate configuration
    config_valid = validate_multi_model_config()
    
    # Test model access if configuration is valid
    if config_valid:
        test_model_access()
    
    print("\n" + "=" * 60)
    print("✅ Validation complete!")
    
    if config_valid:
        print("\n📝 Next Steps:")
        print("1. Implement model factory pattern")
        print("2. Update agent initialization code")
        print("3. Test multi-agent scenarios")
    else:
        print("\n📝 Required Actions:")
        print("1. Complete missing configuration items")
        print("2. Re-run validation")
    
    return config_valid

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
