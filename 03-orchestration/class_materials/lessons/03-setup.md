# Setting up Kestra

Video: [Setting up Kestra](https://www.youtube.com/watch?v=ghkf93rfb2w&list=PL3MmuxUbc_hLZFNgSad56pDBKK8KO0XIv)

Here's how to set up everything you need to run the example flows in this module.

## Prerequisites

This module requires [Docker](https://docs.docker.com/get-started/get-docker/) with Docker Compose to run Kestra locally. [Docker Desktop](https://www.docker.com/products/docker-desktop/) is the easiest way to get both on Mac and Windows. If you don't have Docker installed, set that up before proceeding.

## Step 1: Configure Secrets

Create a `.env` file in the `03-orchestration/class_materials/` directory with your **base64-encoded** API keys. Kestra requires secrets to be base64-encoded:

```bash
cd 03-orchestration/class_materials

# Base64 encode your API keys
export GEMINI_KEY="your_raw_gemini_api_key_here"
export OPENAI_KEY="your_raw_openai_api_key_here"
export TAVILY_KEY="your_raw_tavily_api_key_here"

# Create .env with base64-encoded values
SECRET_GEMINI_API_KEY=$(echo -n "$GEMINI_KEY" | base64)
SECRET_OPENAI_API_KEY=$(echo -n "$OPENAI_KEY" | base64)
SECRET_TAVILY_API_KEY=$(echo -n "$TAVILY_KEY" | base64)

# Add to .env file:
cat >> .env << EOF
SECRET_GEMINI_API_KEY=$SECRET_GEMINI_API_KEY
SECRET_OPENAI_API_KEY=$SECRET_OPENAI_API_KEY
SECRET_TAVILY_API_KEY=$SECRET_TAVILY_API_KEY
EOF
```

> [!NOTE]
> The API keys stored in `.env` must be base64-encoded. Docker Compose will pass them to Kestra as environment variables, and Kestra will automatically decode them when you reference them in flows with `{{ secret('GEMINI_API_KEY') }}`.

## Step 2: Start Kestra

Start the Kestra server:

```bash
cd 03-orchestration/class_materials
docker compose up -d
```

Once the container starts, access the Kestra UI at http://localhost:8080.

To shut down Kestra:

```bash
docker compose down
```

## Step 3: Obtain API Keys

**Gemini API Key (Required)**

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" and copy your key

The free tier is sufficient for light use, but rate limits are relatively low — you may hit quota quickly if you run the agent and multi-agent flows repeatedly. If you run into `429 Resource Exhausted` errors, wait a minute before retrying, or consider upgrading to a paid tier.

**OpenAI API Key (Required for flow 3)**

1. Visit [platform.openai.com](https://platform.openai.com/home) and sign in or create an account
2. Go to **API keys** and create a new key

**Tavily API Key (Required for web search: flows 3, 5, and 6)**

1. Visit [Tavily](https://tavily.com/)
2. Sign up for the free tier
3. Get your API key from the dashboard

The free tier includes 1,000 searches/month.

## Step 4: Reference Secrets in Flows

In your Kestra flows, reference secrets with `{{ secret('GEMINI_API_KEY') }}` — omit the `SECRET_` prefix when calling `secret()`. Kestra will automatically decode the base64-encoded value from the environment and use the raw API key.

> [!WARNING]
> Never commit the `.env` file to Git! Add it to `.gitignore`.

## Step 5: Import Example Flows

```bash
cd 03-orchestration

# Adjust username and password to match your Kestra setup
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/1_chat_without_rag.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/2_chat_with_rag.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/3_rag_with_websearch.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/4_simple_agent.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/5_web_research_agent.yaml
curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/6_multi_agent_research.yaml
```

Alternatively, copy-paste the flow YAML directly into Kestra's UI.

## Step 6: Run Your First Agent

1. Open Kestra UI at http://localhost:8080
2. Navigate to the `zoomcamp` namespace
3. Find the `4_simple_agent` flow and click "Execute"
4. Leave default inputs or customize them
5. Watch the execution and review the outputs
6. Then run `5_web_research_agent` and `6_multi_agent_research` and analyze the logs and outputs

[← Context Engineering](02-context-engineering.md) | [AI Copilot →](04-ai-copilot.md)
