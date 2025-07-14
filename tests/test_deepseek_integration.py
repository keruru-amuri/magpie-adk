#!/usr/bin/env python3
"""
Test script to verify DeepSeek-R1-0528 integration with Azure endpoint.
Tests both LiteLLM approach and azure.ai.inference approach.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deepseek_with_litellm():
    """Test DeepSeek using LiteLLM approach (same as GPT-4.1 series)"""
    print("=" * 60)
    print("Testing DeepSeek with LiteLLM approach...")
    print("=" * 60)
    
    try:
        from google.adk.models.lite_llm import LiteLlm
        
        # Get Azure configuration from environment
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        if not all([azure_api_key, azure_endpoint, azure_api_version]):
            print("❌ Missing Azure configuration in .env file")
            return False
        
        print(f"✓ Azure Endpoint: {azure_endpoint}")
        print(f"✓ API Version: {azure_api_version}")
        print(f"✓ API Key: {'*' * 20}{azure_api_key[-4:] if len(azure_api_key) > 4 else '****'}")
        
        # Set LiteLLM environment variables for Azure
        os.environ["AZURE_API_KEY"] = azure_api_key
        os.environ["AZURE_API_BASE"] = azure_endpoint
        os.environ["AZURE_API_VERSION"] = azure_api_version
        
        # Test with azure/DeepSeek-R1-0528 format
        print("\n🔄 Testing LiteLLM with azure/DeepSeek-R1-0528...")
        model = LiteLlm(model="azure/DeepSeek-R1-0528")
        
        # Simple test completion
        test_messages = [
            {"role": "user", "content": "Hello! Can you tell me what model you are?"}
        ]
        
        print("📤 Sending test message...")
        
        # Import litellm for direct testing
        import litellm
        response = litellm.completion(
            model="azure/DeepSeek-R1-0528",
            messages=test_messages,
            api_key=azure_api_key,
            api_base=azure_endpoint,
            api_version=azure_api_version
        )
        
        print("✅ LiteLLM approach successful!")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ LiteLLM approach failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_deepseek_with_azure_ai_inference():
    """Test DeepSeek using azure.ai.inference approach"""
    print("\n" + "=" * 60)
    print("Testing DeepSeek with azure.ai.inference approach...")
    print("=" * 60)
    
    try:
        from azure.ai.inference import ChatCompletionsClient
        from azure.ai.inference.models import SystemMessage, UserMessage
        from azure.core.credentials import AzureKeyCredential
        
        # Get Azure configuration
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not all([azure_api_key, azure_endpoint]):
            print("❌ Missing Azure configuration")
            return False
        
        # Construct the models endpoint (as shown in your example)
        models_endpoint = azure_endpoint.replace('.openai.azure.com/', '.services.ai.azure.com/models')
        print(f"✓ Models Endpoint: {models_endpoint}")
        
        # Create client
        client = ChatCompletionsClient(
            endpoint=models_endpoint,
            credential=AzureKeyCredential(azure_api_key),
            api_version="2024-05-01-preview"
        )
        
        print("🔄 Testing azure.ai.inference with DeepSeek-R1-0528...")
        
        # Test completion
        response = client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="Hello! Can you tell me what model you are?"),
            ],
            max_tokens=2048,
            model="DeepSeek-R1-0528"
        )
        
        print("✅ azure.ai.inference approach successful!")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ azure.ai.inference approach failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_gpt41_for_comparison():
    """Test GPT-4.1 for comparison to ensure our setup is working"""
    print("\n" + "=" * 60)
    print("Testing GPT-4.1 for comparison...")
    print("=" * 60)
    
    try:
        import litellm
        
        azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        # Set environment variables
        os.environ["AZURE_API_KEY"] = azure_api_key
        os.environ["AZURE_API_BASE"] = azure_endpoint
        os.environ["AZURE_API_VERSION"] = azure_api_version
        
        print("🔄 Testing GPT-4.1 with LiteLLM...")
        
        response = litellm.completion(
            model="azure/gpt-4.1",
            messages=[{"role": "user", "content": "Hello! Can you tell me what model you are?"}],
            api_key=azure_api_key,
            api_base=azure_endpoint,
            api_version=azure_api_version
        )
        
        print("✅ GPT-4.1 working correctly!")
        print(f"📥 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ GPT-4.1 test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 DeepSeek Integration Test Suite")
    print("Testing DeepSeek-R1-0528 with Azure endpoint")
    print("=" * 60)
    
    # Check if required packages are installed
    try:
        import litellm
        print("✓ LiteLLM package available")
    except ImportError:
        print("❌ LiteLLM package not found. Install with: pip install litellm")
        return False
    
    try:
        from azure.ai.inference import ChatCompletionsClient
        print("✓ azure.ai.inference package available")
    except ImportError:
        print("❌ azure.ai.inference package not found. Install with: pip install azure-ai-inference")
        azure_ai_available = False
    else:
        azure_ai_available = True
    
    # Run tests
    results = {}
    
    # Test 1: GPT-4.1 baseline
    results['gpt41'] = test_gpt41_for_comparison()
    
    # Test 2: DeepSeek with LiteLLM
    results['deepseek_litellm'] = test_deepseek_with_litellm()
    
    # Test 3: DeepSeek with azure.ai.inference (if available)
    if azure_ai_available:
        results['deepseek_azure_ai'] = test_deepseek_with_azure_ai_inference()
    else:
        results['deepseek_azure_ai'] = None
        print("\n⚠️  Skipping azure.ai.inference test - package not installed")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"GPT-4.1 (baseline):           {'✅ PASS' if results['gpt41'] else '❌ FAIL'}")
    print(f"DeepSeek + LiteLLM:           {'✅ PASS' if results['deepseek_litellm'] else '❌ FAIL'}")
    
    if results['deepseek_azure_ai'] is not None:
        print(f"DeepSeek + azure.ai.inference: {'✅ PASS' if results['deepseek_azure_ai'] else '❌ FAIL'}")
    else:
        print(f"DeepSeek + azure.ai.inference: ⚠️  SKIPPED")
    
    # Recommendations
    print("\n📋 RECOMMENDATIONS:")
    if results['deepseek_litellm']:
        print("✅ DeepSeek can use LiteLLM approach - same as GPT-4.1 series!")
        print("   → Use: LiteLlm(model='azure/DeepSeek-R1-0528')")
    elif results['deepseek_azure_ai']:
        print("✅ DeepSeek requires azure.ai.inference approach")
        print("   → Need custom wrapper for Google ADK integration")
    else:
        print("❌ DeepSeek integration needs investigation")
        print("   → Check model deployment and endpoint configuration")
    
    return any(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
