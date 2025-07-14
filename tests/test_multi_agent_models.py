#!/usr/bin/env python3
"""
Test script to verify that all agents are using their assigned models correctly.
Tests the multi-model implementation across all agents.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_model_factory():
    """Test the ModelFactory functionality"""
    print("🔧 Testing Model Factory")
    print("=" * 50)
    
    try:
        from common.model_factory import ModelFactory
        
        # Test model configuration validation
        validation_results = ModelFactory.validate_configuration()
        
        print(f"📋 Model Selection Strategy: {validation_results['strategy']}")
        print(f"📋 Available Models: {len(validation_results['available_models'])}")
        
        for model_name, model_config in validation_results['available_models'].items():
            print(f"  ✅ {model_name}: {model_config}")
        
        print(f"📋 Agent Configurations: {len(validation_results['agent_configurations'])}")
        for agent_name, model_config in validation_results['agent_configurations'].items():
            if model_config:
                print(f"  ✅ {agent_name}: {model_config}")
            else:
                print(f"  ⚠️  {agent_name}: Not configured")
        
        if validation_results['issues']:
            print("⚠️  Issues found:")
            for issue in validation_results['issues']:
                print(f"  - {issue}")
        else:
            print("✅ No configuration issues found")
        
        return len(validation_results['issues']) == 0
        
    except Exception as e:
        print(f"❌ Model Factory test failed: {str(e)}")
        return False

def test_agent_model_assignments():
    """Test that each agent gets the correct model assignment"""
    print("\n🤖 Testing Agent Model Assignments")
    print("=" * 50)
    
    try:
        from common.model_factory import ModelFactory
        
        # Expected model assignments based on our configuration
        expected_assignments = {
            'master_coordinator': 'azure/gpt-4.1',
            'general_chat_agent': 'azure/gpt-4.1-mini',
            'query_enhancement_agent': 'azure/gpt-4.1-nano',
            'databricks_query_agent': 'azure/gpt-4.1',
        }
        
        all_correct = True
        
        for agent_name, expected_model in expected_assignments.items():
            model_info = ModelFactory.get_model_info(agent_name)
            actual_model = model_info['model']
            
            if actual_model == expected_model:
                print(f"✅ {agent_name}: {actual_model} (correct)")
            else:
                print(f"❌ {agent_name}: Expected {expected_model}, got {actual_model}")
                all_correct = False
        
        return all_correct
        
    except Exception as e:
        print(f"❌ Agent model assignment test failed: {str(e)}")
        return False

def test_agent_instantiation():
    """Test that agents can be instantiated with their assigned models"""
    print("\n🚀 Testing Agent Instantiation")
    print("=" * 50)
    
    agents_tested = {}
    
    # Test Master Coordinator
    try:
        print("🔄 Testing Master Coordinator...")
        from master_coordinator.agent import root_agent as master_coordinator
        agents_tested['master_coordinator'] = True
        print("✅ Master Coordinator: Instantiated successfully")
    except Exception as e:
        print(f"❌ Master Coordinator: Failed to instantiate - {str(e)}")
        agents_tested['master_coordinator'] = False
    
    # Test General Chat Agent
    try:
        print("🔄 Testing General Chat Agent...")
        from general_chat_agent.agent import root_agent as general_chat_agent
        agents_tested['general_chat_agent'] = True
        print("✅ General Chat Agent: Instantiated successfully")
    except Exception as e:
        print(f"❌ General Chat Agent: Failed to instantiate - {str(e)}")
        agents_tested['general_chat_agent'] = False
    
    # Test Engineering Process Agent (Sequential)
    try:
        print("🔄 Testing Engineering Process Agent...")
        from engineering_process_procedure_agent.agent import root_agent as engineering_agent
        agents_tested['engineering_process_agent'] = True
        print("✅ Engineering Process Agent: Instantiated successfully")
    except Exception as e:
        print(f"❌ Engineering Process Agent: Failed to instantiate - {str(e)}")
        agents_tested['engineering_process_agent'] = False
    
    # Test Sub-Agents individually
    try:
        print("🔄 Testing Query Enhancement Sub-Agent...")
        from engineering_process_procedure_agent.sub_agents.query_enhancement_agent.agent import query_enhancement_agent
        agents_tested['query_enhancement_agent'] = True
        print("✅ Query Enhancement Sub-Agent: Instantiated successfully")
    except Exception as e:
        print(f"❌ Query Enhancement Sub-Agent: Failed to instantiate - {str(e)}")
        agents_tested['query_enhancement_agent'] = False
    
    try:
        print("🔄 Testing Databricks Query Sub-Agent...")
        from engineering_process_procedure_agent.sub_agents.databricks_query_agent.agent import databricks_query_agent
        agents_tested['databricks_query_agent'] = True
        print("✅ Databricks Query Sub-Agent: Instantiated successfully")
    except Exception as e:
        print(f"❌ Databricks Query Sub-Agent: Failed to instantiate - {str(e)}")
        agents_tested['databricks_query_agent'] = False
    
    return all(agents_tested.values())

def test_model_creation():
    """Test creating models for different agents"""
    print("\n🔧 Testing Model Creation")
    print("=" * 50)
    
    try:
        from common.model_factory import create_model_for_agent
        
        test_agents = [
            'master_coordinator',
            'general_chat_agent', 
            'query_enhancement_agent',
            'databricks_query_agent'
        ]
        
        all_successful = True
        
        for agent_name in test_agents:
            try:
                print(f"🔄 Creating model for {agent_name}...")
                model = create_model_for_agent(agent_name)
                print(f"✅ {agent_name}: Model created successfully")
            except Exception as e:
                print(f"❌ {agent_name}: Model creation failed - {str(e)}")
                all_successful = False
        
        return all_successful
        
    except Exception as e:
        print(f"❌ Model creation test failed: {str(e)}")
        return False

def test_environment_configuration():
    """Test that environment is properly configured"""
    print("\n🌍 Testing Environment Configuration")
    print("=" * 50)
    
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT', 
        'AZURE_OPENAI_API_VERSION',
        'MODEL_SELECTION_STRATEGY'
    ]
    
    agent_vars = [
        'MASTER_COORDINATOR_MODEL',
        'GENERAL_CHAT_AGENT_MODEL',
        'QUERY_ENHANCEMENT_AGENT_MODEL',
        'DATABRICKS_QUERY_AGENT_MODEL'
    ]
    
    all_configured = True
    
    print("📋 Required Environment Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            display_value = f"{'*' * 20}{value[-4:]}" if 'KEY' in var and len(value) > 4 else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: Not set")
            all_configured = False
    
    print("\n📋 Agent-Specific Model Variables:")
    for var in agent_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set (will use fallback)")
    
    return all_configured

def main():
    """Run all tests"""
    print("🚀 Multi-Agent Model Implementation Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_results = {}
    
    test_results['environment'] = test_environment_configuration()
    test_results['model_factory'] = test_model_factory()
    test_results['model_assignments'] = test_agent_model_assignments()
    test_results['model_creation'] = test_model_creation()
    test_results['agent_instantiation'] = test_agent_instantiation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    overall_success = all(test_results.values())
    
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Multi-model implementation is working correctly!")
        print("📝 All agents are properly configured with their assigned models:")
        print("  • Master Coordinator: GPT-4.1 (strong routing decisions)")
        print("  • General Chat Agent: GPT-4.1-mini (cost-effective conversation)")
        print("  • Query Enhancement: GPT-4.1-nano (focused enhancement)")
        print("  • Databricks Query: GPT-4.1 (technical processing)")
    else:
        print("\n⚠️  Some issues were found. Please review the test output above.")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
