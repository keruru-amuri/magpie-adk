"""
Test script for table metadata integration

This script demonstrates both approaches for adding table context:
1. Script-based approach using CSV files
2. Interactive approach using the Data Scientist Agent
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_scientist_agent.mcp_client import (
    get_table_metadata_sync, set_table_context_sync, load_context_from_csv_sync
)


def test_script_approach():
    """Test the script-based approach using CSV files."""
    print("🧪 Testing Script-Based Approach")
    print("=" * 50)
    
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "table_context", 
        "ac_utilization_sample.csv"
    )
    table_name = "engineering.silver.ac_utilization"
    
    print(f"📄 CSV Path: {csv_path}")
    print(f"🎯 Target Table: {table_name}")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        print("💡 Create the CSV file first using the sample format")
        return False
    
    try:
        result = load_context_from_csv_sync(csv_path, table_name)
        
        if result.get("status") == "success":
            print("✅ Successfully loaded context from CSV")
            print(f"   Message: {result.get('message')}")
            
            # Show what was loaded
            context = result.get("context", {})
            print(f"   Business context items: {len(context.get('business_context', {}))}")
            print(f"   Field mappings: {len(context.get('field_mappings', {}))}")
            print(f"   Transformations: {len(context.get('transformations', {}))}")
            print(f"   Common queries: {len(context.get('common_queries', []))}")
            
            return True
        else:
            print(f"❌ Failed to load context: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_interactive_approach():
    """Test the interactive approach using agent tools."""
    print("\n🤖 Testing Interactive Approach")
    print("=" * 50)
    
    table_name = "engineering.silver.ac_utilization"
    
    # Test setting context manually
    sample_context = {
        "business_context": {
            "description": "Aircraft utilization data from AMOS system",
            "source_system": "AMOS",
            "update_frequency": "Daily batch at 02:00 UTC"
        },
        "field_mappings": {
            "ac_reg": {
                "description": "Aircraft registration number (tail number)",
                "notes": "Format: 9M-XXX for Malaysia Airlines"
            },
            "flight_hours": {
                "description": "Total flight hours for the aircraft",
                "notes": "Decimal hours, includes taxi time"
            }
        },
        "transformations": {
            "flight_date_int": {
                "rule": "YYYYMMDD integer format",
                "description": "Convert to date: CAST(CAST(flight_date_int AS STRING) AS DATE)"
            }
        },
        "common_queries": [
            {
                "intent": "monthly_utilization",
                "template": "SELECT ac_reg, SUM(flight_hours) as total_hours FROM {table} WHERE flight_date_int >= {start_date_int} GROUP BY ac_reg",
                "description": "Get monthly utilization by aircraft"
            }
        ]
    }
    
    try:
        print(f"🎯 Setting context for table: {table_name}")
        result = set_table_context_sync(table_name, sample_context)
        
        if result.get("status") == "success":
            print("✅ Successfully set table context")
            
            # Now test retrieving the context
            print("📖 Retrieving table metadata...")
            metadata_result = get_table_metadata_sync(table_name)
            
            if metadata_result.get("status") == "success":
                print("✅ Successfully retrieved table metadata")
                metadata = metadata_result.get("data", {})
                print(f"   Table: {metadata.get('table_name')}")
                print(f"   Has MAGPIE context: {metadata.get('has_magpie_context', False)}")
            else:
                print(f"⚠️ Could not retrieve metadata: {metadata_result.get('error')}")
            
            return True
        else:
            print(f"❌ Failed to set context: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_agent_integration():
    """Test that the agent has the new metadata tools."""
    print("\n🔧 Testing Agent Integration")
    print("=" * 50)
    
    try:
        from data_scientist_agent.agent import data_scientist_agent
        
        if data_scientist_agent is None:
            print("❌ Agent not created")
            return False
        
        tools = data_scientist_agent.tools
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in tools]
        
        print(f"✅ Agent has {len(tools)} tools")
        
        expected_metadata_tools = [
            "get_table_metadata_sync",
            "set_table_context_sync", 
            "load_context_from_csv_sync"
        ]
        
        for tool in expected_metadata_tools:
            if tool in tool_names:
                print(f"   ✅ {tool} - Available")
            else:
                print(f"   ❌ {tool} - Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False


def show_usage_examples():
    """Show usage examples for both approaches."""
    print("\n💡 Usage Examples")
    print("=" * 50)
    
    print("📋 Option 1: Script-Based Approach")
    print("   1. Create CSV file with table context:")
    print("      data_scientist_agent/table_context/ac_utilization.csv")
    print("   2. Run script:")
    print("      python data_scientist_agent/scripts/load_table_context.py \\")
    print("        --csv data_scientist_agent/table_context/ac_utilization.csv \\")
    print("        --table engineering.silver.ac_utilization \\")
    print("        --execute")
    
    print("\n🤖 Option 2: Interactive Agent Approach")
    print("   Ask the Data Scientist Agent:")
    print("   • 'Load context from CSV file for engineering.silver.ac_utilization'")
    print("   • 'Set table context for engineering.silver.ac_utilization'")
    print("   • 'Get metadata for engineering.silver.ac_utilization'")
    
    print("\n📝 CSV Format Required:")
    print("   context_type,key,value,description")
    print("   business_context,description,\"Table description\",\"Main description\"")
    print("   field_mapping,field_name,\"Field description\",\"Additional notes\"")
    print("   transformation,field_name,\"Transformation rule\",\"How to apply\"")


def main():
    """Main test function."""
    print("🚀 Table Metadata Integration Test Suite")
    print("=" * 60)
    
    # Test agent integration first
    agent_ok = test_agent_integration()
    
    if not agent_ok:
        print("\n❌ Agent integration failed. Fix agent setup first.")
        return False
    
    # Test interactive approach (doesn't require CSV file)
    interactive_ok = test_interactive_approach()
    
    # Test script approach (requires CSV file)
    script_ok = test_script_approach()
    
    # Show usage examples
    show_usage_examples()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"Agent Integration: {'✅' if agent_ok else '❌'}")
    print(f"Interactive Approach: {'✅' if interactive_ok else '❌'}")
    print(f"Script Approach: {'✅' if script_ok else '⚠️ (requires CSV file)'}")
    
    if agent_ok and interactive_ok:
        print("\n🎉 Metadata integration is working!")
        print("You can now use both approaches to add table context.")
    else:
        print("\n⚠️ Some tests failed. Check the configuration.")
    
    return agent_ok and interactive_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
