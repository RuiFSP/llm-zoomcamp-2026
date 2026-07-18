"""
Query Logfire traces in DuckDB to sum input tokens (Q3).

This script connects to the DuckDB database created by dlt and 
sums the input tokens from all LLM calls within the traces.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
root_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=root_env, override=True)

import duckdb


def query_tokens():
    """
    Query DuckDB for input token usage from Logfire traces.
    
    The token counts are stored in span attributes as 'gen_ai.usage.input_tokens'.
    We sum them across all LLM calls within a trace.
    """
    # Connect to the DuckDB database created by dlt
    db_path = '.dlt/agent_traces/agent_traces.duckdb'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please run load_traces.py first")
        return
    
    conn = duckdb.connect(db_path)
    
    # Try to query the spans table and extract token information
    try:
        # First, let's see what tables we have
        tables = conn.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'agent_traces' ORDER BY table_name"
        ).fetchall()
        print("Available tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # List columns in spans table to understand structure
        columns = conn.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'agent_traces' AND table_name = 'spans'"
        ).fetchall()
        print("\nSpans table columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        # Query for token usage in span attributes
        # The structure may vary, so we'll try a few approaches
        print("\n" + "="*60)
        print("Attempting to find input token usage...")
        print("="*60)
        
        # Try to find spans with token data
        result = conn.execute("""
            SELECT span_name, attributes 
            FROM agent_traces.spans 
            WHERE attributes LIKE '%input_tokens%' OR attributes LIKE '%usage%'
            LIMIT 5
        """).fetchall()
        
        if result:
            print(f"\nFound {len(result)} spans with token data:")
            for span_name, attrs in result:
                print(f"  Span: {span_name}")
                print(f"  Attributes: {attrs[:200]}...")
        else:
            print("\nNo token data found. Showing sample span data:")
            sample = conn.execute("""
                SELECT span_name, attributes 
                FROM agent_traces.spans 
                LIMIT 3
            """).fetchall()
            for span_name, attrs in sample:
                print(f"  Span: {span_name}")
                print(f"  Attributes: {attrs[:300] if attrs else 'None'}...")
        
        # Try to sum tokens if they exist as a column
        try:
            total_tokens = conn.execute("""
                SELECT SUM(CAST(attributes->'gen_ai'->'usage'->'input_tokens' AS INTEGER)) as total_input_tokens
                FROM agent_traces.spans
                WHERE attributes->'gen_ai'->'usage'->'input_tokens' IS NOT NULL
            """).fetchone()
            
            if total_tokens and total_tokens[0]:
                print(f"\n✅ Total input tokens: {total_tokens[0]}")
                
                # Categorize the result
                tokens = total_tokens[0]
                if 100 <= tokens <= 500:
                    print("  → Answer range: 100 - 500")
                elif 1500 <= tokens <= 5000:
                    print("  → Answer range: 1500 - 5000")
                elif 10000 <= tokens <= 20000:
                    print("  → Answer range: 10000 - 20000")
                elif 50000 <= tokens <= 100000:
                    print("  → Answer range: 50000 - 100000")
                else:
                    print(f"  → Answer range: {tokens} (outside provided ranges)")
        except Exception as e:
            print(f"\nNote: Could not query nested token data: {e}")
            print("The exact column structure may differ from expected.")
        
        conn.close()
    
    except Exception as e:
        print(f"Error querying database: {e}")
        conn.close()


if __name__ == '__main__':
    query_tokens()
