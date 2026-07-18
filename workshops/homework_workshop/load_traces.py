"""
Load Logfire traces into DuckDB using dlt.

This script pulls the Logfire API data and normalizes it into DuckDB tables.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
root_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=root_env, override=True)

import requests
import json
import dlt


def logfire_source():
    """
    Fetch Logfire trace data via the Logfire API.
    """
    read_token = os.getenv('LOGFIRE_READ_TOKEN')
    if not read_token:
        raise ValueError('LOGFIRE_READ_TOKEN not set in .env')
    
    headers = {'Authorization': f'Bearer {read_token}'}
    
    @dlt.resource(name='spans', write_disposition='replace')
    def get_spans():
        """Fetch all spans from Logfire."""
        # Try different Logfire API endpoints
        endpoints = [
            'https://api.logfire.dev/api/v1/read/trace_report',
            'https://api.logfire.dev/api/v1/read/spans',
            'https://api.logfire.dev/api/v1/traces',
        ]
        
        for endpoint in endpoints:
            try:
                print(f"Trying endpoint: {endpoint}")
                response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"Got data from {endpoint}")
                    
                    if isinstance(data, list):
                        for item in data:
                            yield item
                    elif isinstance(data, dict):
                        items = data.get('data', []) or data.get('spans', []) or data.get('traces', [])
                        for item in items:
                            yield item
                    break
            except Exception as e:
                print(f"Failed {endpoint}: {e}")
                continue


def load_to_duckdb():
    """Initialize dlt pipeline and load Logfire data to DuckDB."""
    print("Initializing dlt pipeline...")
    pipeline = dlt.pipeline(
        pipeline_name='agent_traces',
        destination='duckdb',
        dataset_name='agent_traces'
    )
    
    print("Fetching Logfire data...")
    source = logfire_source()
    
    try:
        load_info = pipeline.run(source)
        print(f"Load info: {load_info}")
    except Exception as e:
        print(f"Load failed: {e}")
        print("Note: If Logfire API isn't accessible, this is expected.")
        print("For Q2 and Q3, check your Logfire dashboard directly or use the web interface.")
    
    # Check tables created using DuckDB directly
    import duckdb
    db_path = '.dlt/agent_traces/agent_traces.duckdb'
    
    try:
        if os.path.exists(db_path):
            conn = duckdb.connect(db_path)
            
            # List tables
            tables = conn.execute(
                "SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'agent_traces';"
            ).fetchall()
            
            print(f"\n✅ Tables created: {tables[0][0]}")
            
            # List table names
            all_tables = conn.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'agent_traces' ORDER BY table_name;"
            ).fetchall()
            
            print("\nTable list:")
            for row in all_tables:
                print(f"  - {row[0]}")
            
            conn.close()
        else:
            print(f"\nDatabase not yet created at {db_path}")
            print("The API may not have returned data, or the endpoint is not accessible.")
    except Exception as e:
        print(f"Error querying database: {e}")


if __name__ == '__main__':
    load_to_duckdb()
