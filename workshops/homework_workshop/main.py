import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
root_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=root_env, override=True)

import logfire
from openai import OpenAI
from opentelemetry import trace
from ingest import build_index, load_faq_data


def main():
    # Setup OpenTelemetry tracing
    print("Initializing Logfire tracing...")
    if os.getenv('LOGFIRE_TOKEN'):
        logfire.configure(token=os.getenv('LOGFIRE_TOKEN'))
    
    tracer = trace.get_tracer(__name__)
    
    # Download FAQ and build index
    print("Loading FAQ data...")
    documents = load_faq_data()
    print(f"Loaded {len(documents)} documents")
    
    print("Building index...")
    index = build_index(documents)
    print("Index built")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Create tools for the agent
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_faq",
                "description": "Search the FAQ database for relevant information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    ]
    
    def search_faq(query):
        """Search the FAQ index"""
        boost_dict = {'question': 3.0, 'section': 0.5}
        filter_dict = {'course': 'llm-zoomcamp'}
        results = index.search(query, num_results=5, boost_dict=boost_dict, filter_dict=filter_dict)
        return json.dumps(results)
    
    # Agent loop with tracing
    print("\nRunning agent with Logfire instrumentation...")
    question = 'How do I run Ollama locally?'
    messages = [{"role": "user", "content": question}]
    
    span_count = 0
    with tracer.start_as_current_span("agent_run") as main_span:
        span_count += 1
        print(f"[Span {span_count}] Agent run started")
        
        # Agent loop - typically makes 1-3 tool calls
        max_iterations = 5
        for iteration in range(max_iterations):
            with tracer.start_as_current_span(f"llm_call_{iteration}") as llm_span:
                span_count += 1
                print(f"[Span {span_count}] LLM call {iteration}")
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
            
            messages.append({
                "role": "assistant",
                "content": response.choices[0].message.content or "",
                "tool_calls": getattr(response.choices[0].message, 'tool_calls', None)
            })
            
            # Check if model wants to use a tool
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    with tracer.start_as_current_span(f"tool_call_{tool_call.function.name}") as tool_span:
                        span_count += 1
                        print(f"[Span {span_count}] Tool call: {tool_call.function.name}")
                        
                        # Execute the tool
                        if tool_call.function.name == "search_faq":
                            result = search_faq(json.loads(tool_call.function.arguments)["query"])
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result
                            })
            else:
                # Model finished, no more tool calls
                break
        
        # Get final answer
        with tracer.start_as_current_span("final_response") as final_span:
            span_count += 1
            print(f"[Span {span_count}] Final response")
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
    
    print(f"\n✅ Agent run complete!")
    print(f"Total spans created: {span_count}")
    print(f"Final answer: {response.choices[0].message.content}\n")
    print("Check your Logfire dashboard for the full trace visualization!")


if __name__ == '__main__':
    main()
