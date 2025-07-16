"""
Script to load table context from CSV and apply to Databricks table metadata.

This script reads table context information from CSV files and applies them
as Unity Catalog table properties for the Data Scientist Agent to use.
"""

import os
import sys
import pandas as pd
import json
import asyncio
from typing import Dict, Any, Optional

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from data_scientist_agent.mcp_client import execute_sql_sync


def load_context_from_csv(csv_path: str) -> Dict[str, Any]:
    """
    Load table context from CSV file.
    
    Expected CSV format:
    - context_type, key, value, description
    - business_context, description, "Aircraft utilization data from AMOS", "Main table description"
    - field_mapping, ac_reg, "Aircraft registration number", "Field description"
    - transformation, flight_date_int, "YYYYMMDD format", "Date transformation rule"
    """
    try:
        df = pd.read_csv(csv_path)
        
        context = {
            "business_context": {},
            "field_mappings": {},
            "transformations": {},
            "common_queries": []
        }
        
        for _, row in df.iterrows():
            context_type = row['context_type']
            key = row['key']
            value = row['value']
            description = row.get('description', '')
            
            if context_type == 'business_context':
                context['business_context'][key] = value
            elif context_type == 'field_mapping':
                context['field_mappings'][key] = {
                    "description": value,
                    "notes": description
                }
            elif context_type == 'transformation':
                context['transformations'][key] = {
                    "rule": value,
                    "description": description
                }
            elif context_type == 'common_query':
                context['common_queries'].append({
                    "intent": key,
                    "template": value,
                    "description": description
                })
        
        return context
        
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return {}


def generate_metadata_sql(table_name: str, context: Dict[str, Any]) -> str:
    """Generate SQL to set table properties with context metadata."""
    
    # Escape JSON for SQL
    business_context_json = json.dumps(context.get('business_context', {})).replace("'", "''")
    field_mappings_json = json.dumps(context.get('field_mappings', {})).replace("'", "''")
    transformations_json = json.dumps(context.get('transformations', {})).replace("'", "''")
    common_queries_json = json.dumps(context.get('common_queries', [])).replace("'", "''")
    
    sql = f"""
-- Set table metadata for {table_name}
ALTER TABLE {table_name} 
SET TBLPROPERTIES (
    'magpie.business_context' = '{business_context_json}',
    'magpie.field_mappings' = '{field_mappings_json}',
    'magpie.transformations' = '{transformations_json}',
    'magpie.common_queries' = '{common_queries_json}',
    'magpie.last_updated' = '{pd.Timestamp.now().isoformat()}',
    'magpie.version' = '1.0'
);
"""
    
    return sql


def apply_metadata_to_table(table_name: str, context: Dict[str, Any], execute: bool = False) -> str:
    """
    Apply metadata context to Databricks table.
    
    Args:
        table_name: Full table name (catalog.schema.table)
        context: Context dictionary from CSV
        execute: Whether to actually execute the SQL (default: False, just return SQL)
    
    Returns:
        SQL statement that was generated/executed
    """
    sql = generate_metadata_sql(table_name, context)
    
    if execute:
        try:
            result = execute_sql_sync(sql)
            if result.get('status') == 'success':
                print(f"✅ Successfully applied metadata to {table_name}")
            else:
                print(f"❌ Error applying metadata: {result.get('error')}")
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
    else:
        print("📋 Generated SQL (use --execute to apply):")
        print(sql)
    
    return sql


def create_sample_csv(output_path: str):
    """Create a sample CSV file showing the expected format."""
    sample_data = [
        {
            'context_type': 'business_context',
            'key': 'description',
            'value': 'Aircraft utilization data from AMOS system showing flight hours and cycles',
            'description': 'Main table description'
        },
        {
            'context_type': 'business_context', 
            'key': 'source_system',
            'value': 'AMOS',
            'description': 'Source system identifier'
        },
        {
            'context_type': 'business_context',
            'key': 'update_frequency', 
            'value': 'Daily batch at 02:00 UTC',
            'description': 'How often data is refreshed'
        },
        {
            'context_type': 'field_mapping',
            'key': 'ac_reg',
            'value': 'Aircraft registration number (tail number)',
            'description': 'Format: 9M-XXX for Malaysia Airlines'
        },
        {
            'context_type': 'field_mapping',
            'key': 'flight_hours',
            'value': 'Total flight hours for the aircraft',
            'description': 'Decimal hours, includes taxi time'
        },
        {
            'context_type': 'transformation',
            'key': 'flight_date_int',
            'value': 'YYYYMMDD integer format',
            'description': 'Convert to date: CAST(CAST(flight_date_int AS STRING) AS DATE)'
        },
        {
            'context_type': 'common_query',
            'key': 'monthly_utilization',
            'value': 'SELECT ac_reg, SUM(flight_hours) as total_hours FROM {table} WHERE flight_date_int >= {start_date_int} GROUP BY ac_reg',
            'description': 'Get monthly utilization by aircraft'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv(output_path, index=False)
    print(f"📄 Sample CSV created at: {output_path}")


def main():
    """Main function to handle command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Load table context from CSV to Databricks metadata')
    parser.add_argument('--csv', required=True, help='Path to CSV file with context data')
    parser.add_argument('--table', required=True, help='Full table name (catalog.schema.table)')
    parser.add_argument('--execute', action='store_true', help='Execute the SQL (default: just show SQL)')
    parser.add_argument('--create-sample', help='Create a sample CSV file at specified path')
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_csv(args.create_sample)
        return
    
    # Load context from CSV
    print(f"📖 Loading context from: {args.csv}")
    context = load_context_from_csv(args.csv)
    
    if not context:
        print("❌ Failed to load context from CSV")
        return
    
    print(f"✅ Loaded context with {len(context.get('field_mappings', {}))} field mappings")
    
    # Apply to table
    print(f"🎯 Applying context to table: {args.table}")
    apply_metadata_to_table(args.table, context, execute=args.execute)


if __name__ == "__main__":
    main()
