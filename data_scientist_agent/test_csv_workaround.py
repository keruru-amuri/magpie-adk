"""
Test CSV processing workaround for file upload limitations
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from data_scientist_agent.mcp_client import (
    read_csv_content_sync, parse_csv_content_only_sync
)


def test_csv_content_reading():
    """Test reading CSV content from file path."""
    print("🧪 Testing CSV Content Reading")
    print("=" * 50)
    
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "table_context", 
        "ac_utilization_sample.csv"
    )
    
    print(f"📄 Reading CSV: {csv_path}")
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    result = read_csv_content_sync(csv_path)
    
    if result.get("status") == "success":
        data = result.get("data", {})
        print("✅ Successfully read CSV content")
        print(f"   Total rows: {data.get('summary', {}).get('total_rows')}")
        print(f"   Columns: {data.get('summary', {}).get('columns')}")
        print(f"   Is table context: {data.get('is_table_context')}")
        
        if data.get("is_table_context"):
            context_summary = data.get("context_summary", {})
            print(f"   Business context items: {context_summary.get('business_context_items')}")
            print(f"   Field mappings: {context_summary.get('field_mappings')}")
            print(f"   Transformations: {context_summary.get('transformations')}")
        
        print("\n📝 Formatted text preview (first 500 chars):")
        formatted_text = data.get("formatted_text", "")
        print(formatted_text[:500] + "..." if len(formatted_text) > 500 else formatted_text)
        
        return True
    else:
        print(f"❌ Failed to read CSV: {result.get('error')}")
        return False


def test_csv_text_processing():
    """Test parsing CSV content provided as text (without applying to Databricks)."""
    print("\n🧪 Testing CSV Text Parsing")
    print("=" * 50)

    # Sample CSV content as text (what user would paste)
    csv_text = """context_type,key,value,description
business_context,description,Test aircraft utilization data,Main table description
business_context,source_system,TEST_SYSTEM,Source system identifier
field_mapping,ac_registr,Aircraft registration number,Format: 9M-XXX for Malaysia Airlines
field_mapping,departure_date,Flight departure date,Date when flight departed
transformation,departure_date,Date format YYYY-MM-DD,Standard date format
common_query,test_query,SELECT * FROM {table} LIMIT 10,Sample query for testing"""

    print(f"📝 CSV content length: {len(csv_text)} characters")
    print("🔍 Parsing CSV content (validation only)...")

    result = parse_csv_content_only_sync(csv_text)

    if result.get("status") == "success":
        print("✅ Successfully parsed CSV text")
        print(f"   Rows processed: {result.get('rows_processed')}")

        summary = result.get("summary", {})
        print(f"   Business context items: {summary.get('business_context_items')}")
        print(f"   Field mappings: {summary.get('field_mappings')}")
        print(f"   Transformations: {summary.get('transformations')}")
        print(f"   Common queries: {summary.get('common_queries')}")

        # Show parsed context preview
        context = result.get("context", {})
        print("\n📋 Parsed Context Preview:")
        if context.get("business_context"):
            print(f"   Business: {context['business_context']}")
        if context.get("field_mappings"):
            print(f"   Fields: {list(context['field_mappings'].keys())}")

        return True
    else:
        print(f"❌ Failed to parse CSV text: {result.get('error')}")
        return False


def show_usage_examples():
    """Show usage examples for the CSV workaround."""
    print("\n💡 CSV Upload Workaround Usage")
    print("=" * 50)
    
    print("🚫 Problem: File upload gives error:")
    print('   {"error": "LiteLlm(BaseLlm) does not support this content part."}')
    
    print("\n✅ Solution 1: Paste CSV content as text")
    print("   User: 'I have this CSV content for table metadata:'")
    print("   User: [pastes CSV content as text]")
    print("   Agent: Uses parse_csv_content_only_sync(csv_text) then process_csv_for_table_context_sync(csv_text, table_name)")
    
    print("\n✅ Solution 2: Provide file path")
    print("   User: 'Load context from file data_scientist_agent/table_context/ac_utilization.csv'")
    print("   Agent: Uses read_csv_content_sync(file_path) then processes content")
    
    print("\n📋 Agent Response Template:")
    print('   "Due to file upload limitations, please either:')
    print('   1. Copy and paste your CSV content as text, or')
    print('   2. Provide the file path if it\'s accessible on the system"')


def main():
    """Main test function."""
    print("🚀 CSV Processing Workaround Test Suite")
    print("=" * 60)
    
    # Test reading from file path
    file_reading_ok = test_csv_content_reading()
    
    # Test processing text content
    text_processing_ok = test_csv_text_processing()
    
    # Show usage examples
    show_usage_examples()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"File Reading: {'✅' if file_reading_ok else '❌'}")
    print(f"Text Processing: {'✅' if text_processing_ok else '❌'}")
    
    if file_reading_ok and text_processing_ok:
        print("\n🎉 CSV workaround is working!")
        print("Users can now work around file upload limitations.")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")
    
    return file_reading_ok and text_processing_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
