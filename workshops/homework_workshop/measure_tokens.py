#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load from root env
root_env = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=root_env, override=True)

import logfire
from openai import OpenAI
from opentelemetry import trace
from ingest import build_index, load_faq_data
import json

# Setup
logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
tracer = trace.get_tracer(__name__)

# Load FAQ
print("Loading FAQ...")
documents = load_faq_data()
index = build_index(documents)

# Initialize OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Run query
question = 'How do I run Ollama locally?'
messages = [{"role": "user", "content": question}]

tools = [{
    "type": "function",
    "function": {
        "name": "search_faq",
        "description": "Search FAQ",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    }
}]

def search_faq(query):
    boost_dict = {'question': 3.0, 'section': 0.5}
    filter_dict = {'course': 'llm-zoomcamp'}
    results = index.search(query, num_results=5, boost_dict=boost_dict, filter_dict=filter_dict)
    return json.dumps(results)

span_count = 0
token_info = []

print("Running agent with tracing...")
with tracer.start_as_current_span("agent_run"):
    span_count += 1
    
    for iteration in range(5):
        with tracer.start_as_current_span(f"llm_call_{iteration}"):
            span_count += 1
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            
            # Track token usage
            if response.usage:
                print(f"LLM Call {iteration}: input={response.usage.prompt_tokens}, output={response.usage.completion_tokens}")
                token_info.append({
                    'call': iteration,
                    'input': response.usage.prompt_tokens,
                    'output': response.usage.completion_tokens
                })
        
        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content or "",
            "tool_calls": getattr(response.choices[0].message, 'tool_calls', None)
        })
        
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                with tracer.start_as_current_span(f"tool_call_{tool_call.function.name}"):
                    span_count += 1
                    result = search_faq(json.loads(tool_call.function.arguments)["query"])
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
        else:
            break
    
    with tracer.start_as_current_span("final_response"):
        span_count += 1
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        if response.usage:
            print(f"Final Response: input={response.usage.prompt_tokens}, output={response.usage.completion_tokens}")
            token_info.append({
                'call': 'final',
                'input': response.usage.prompt_tokens,
                'output': response.usage.completion_tokens
            })

print(f"\n✅ Total spans: {span_count}")
print(f"\nToken Breakdown:")
for info in token_info:
    print(f"  {info['call']}: {info['input']} input tokens")
    
total_input = sum(t['input'] for t in token_info)
print(f"\n📊 Total input tokens: {total_input}")

# Categorize
if 100 <= total_input <= 500:
    print("Answer: 100-500")
elif 1500 <= total_input <= 5000:
    print("Answer: 1500-5000")
elif 10000 <= total_input <= 20000:
    print("Answer: 10000-20000")
elif 50000 <= total_input <= 100000:
    print("Answer: 50000-100000")
else:
    print(f"Answer: {total_input} (outside ranges)")
