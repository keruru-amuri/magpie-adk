#!/usr/bin/env python3
"""
Test DeepSeek model with timeout configurations
"""

import os
import asyncio
from dotenv import load_dotenv
from common.model_factory import ModelFactory

load_dotenv()

async def test_deepseek_with_timeout():
    """Test DeepSeek model with proper timeout configuration."""
    print("Testing DeepSeek Model with Timeout Configuration")
    print("=" * 60)
    
    try:
        # Get model info for data scientist agent
        model_info = ModelFactory.get_model_info('data_scientist_agent')
        print(f"Model Configuration:")
        print(f"  Agent: {model_info['agent_name']}")
        print(f"  Model: {model_info['model']}")
        print(f"  Strategy: {model_info['strategy']}")
        print(f"  Source: {model_info['source']}")
        
        # Create the model with timeout configuration
        print(f"\nCreating model instance...")
        model = ModelFactory.create_model('data_scientist_agent')
        print(f"✅ Model created successfully: {model}")
        
        # Test a simple completion
        print(f"\nTesting simple completion...")
        from google.genai import types
        
        test_content = types.Content(
            role='user', 
            parts=[types.Part(text="Hello! Please respond with just 'Hello from DeepSeek' to test the connection.")]
        )
        
        print("📤 Sending test message...")
        
        # Use async generation
        response_generator = model.generate_content_async([test_content])
        
        # Get the first response with timeout
        try:
            response = await asyncio.wait_for(
                response_generator.__anext__(), 
                timeout=180  # 3 minutes timeout
            )
            
            print("✅ DeepSeek response received!")
            print(f"📥 Response: {response}")
            return True
            
        except asyncio.TimeoutError:
            print("❌ Request timed out after 3 minutes")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_configuration():
    """Test the configuration values."""
    print("\nConfiguration Check:")
    print("=" * 30)
    
    config_vars = [
        'DATA_SCIENTIST_AGENT_MODEL',
        'LITELLM_REQUEST_TIMEOUT', 
        'LITELLM_MAX_RETRIES',
        'DEEPSEEK_TIMEOUT',
        'DEEPSEEK_MAX_TOKENS'
    ]
    
    for var in config_vars:
        value = os.getenv(var, 'Not set')
        print(f"  {var}: {value}")

async def main():
    """Main test function."""
    print("DeepSeek Timeout Configuration Test")
    print("=" * 60)
    
    # Test configuration
    test_configuration()
    
    # Test DeepSeek with timeout
    success = await test_deepseek_with_timeout()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 DeepSeek timeout test PASSED!")
        print("The data scientist agent should now work with DeepSeek.")
    else:
        print("❌ DeepSeek timeout test FAILED!")
        print("Consider switching back to GPT-4.1 or investigating further.")
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        exit(1)
