import dlt
import json

# Create sample OpenTelemetry span data
sample_spans = [
    {
        "name": "agent_run",
        "span_id": "123456",
        "trace_id": "abcdef",
        "start_time": 1234567890,
        "end_time": 1234567895,
        "duration_ms": 5000,
        "attributes": {
            "span.kind": "internal",
            "service.name": "agent"
        },
        "events": []
    },
    {
        "name": "llm_call",
        "span_id": "234567",
        "trace_id": "abcdef",
        "start_time": 1234567890,
        "end_time": 1234567893,
        "duration_ms": 3000,
        "attributes": {
            "gen_ai.usage.input_tokens": 1335,
            "gen_ai.usage.output_tokens": 337
        },
        "events": []
    }
]

@dlt.resource(name='spans', write_disposition='replace')
def get_spans():
    for span in sample_spans:
        yield span

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name='test_traces',
    destination='duckdb',
    dataset_name='test_traces'
)

# Load data
print("Loading sample traces...")
pipeline.run(get_spans())

# Check tables created
import duckdb
conn = duckdb.connect('.dlt/test_traces/test_traces.duckdb')

# List all tables
tables = conn.execute(
    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'test_traces' ORDER BY table_name"
).fetchall()

print(f"\n✅ Number of tables created by dlt: {len(tables)}")
print("\nTables:")
for i, (table_name,) in enumerate(tables, 1):
    print(f"  {i}. {table_name}")

conn.close()
