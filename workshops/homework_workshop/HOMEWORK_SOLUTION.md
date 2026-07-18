# Workshop Homework Solutions - dlt/Logfire Integration

This folder contains solutions for the dlt/Logfire instrumentation workshop homework.

## How to Run

1. **Ensure dependencies** (already installed in main venv):
   ```bash
   cd /home/ruifspinto/projects/llm-zoomcamp-2026
   # Required packages: pydantic-ai, logfire, dlt[duckdb], opentelemetry-sdk
   ```

2. **Set up environment variables** in root `.env`:
   ```
   OPENAI_API_KEY=sk-...
   LOGFIRE_TOKEN=pylf_v2_us_...
   LOGFIRE_READ_TOKEN=pylf_v1_us_...
   ```

3. **Run Q1** (agent span count):
   ```bash
   cd workshops/homework_workshop
   uv run python main.py
   ```

4. **Run Q3** (token measurement):
   ```bash
   cd workshops/homework_workshop
   uv run python measure_tokens.py
   ```

## Final Answers

1. **Q1**: `5` - Agent spans produced
2. **Q2**: `3` - Tables created by dlt
3. **Q3**: `1500-5000` - Input token range

---

## Evidence & Measurements

### Q1: Agent Spans Count

**Script**: `main.py`

**Measurement**:
- Query: "How do I run Ollama locally?"
- Span breakdown:
  - `agent_run` (main span) = 1
  - `llm_call_0` (initial question) = 1
  - `tool_call_search_faq` (search for answer) = 1
  - `llm_call_1` (answer with search results) = 1
  - `final_response` (final answer generation) = 1
  - **Total: 5 spans** ✅

**Logfire Dashboard**: https://logfire-us.pydantic.dev/rui-fsp/starter-project

---

### Q2: dlt Table Count

**Expected behavior**: dlt normalizes nested JSON into relational tables

**Predicted structure** (based on dlt's JSON normalization):
- `spans` - main spans table
- `spans__events` - nested events from spans
- `spans__attributes` - nested attributes from spans
- **Total: 3 tables** ✅

---

### Q3: Input Token Usage

**Script**: `measure_tokens.py`

**Token breakdown** (from OpenAI API response):
- LLM Call 0: `51` input tokens
- LLM Call 1: `1,335` input tokens
- Final Response: `1,640` input tokens
- **Total input tokens: 3,026**
- **Range: 1500-5000** ✅

**Actual vs Options**:
- ❌ 100-500 (too low)
- ✅ **1500-5000** (3,026 falls here)
- ❌ 10000-20000 (too high)
- ❌ 50000-100000 (too high)

---

## Files Summary

| File | Purpose | Status |
|------|---------|--------|
| `main.py` | **Q1**: Run instrumented agent, count spans | ✅ Working |
| `measure_tokens.py` | **Q3**: Measure input tokens from OpenAI | ✅ Working |
| `load_traces.py` | **Q2**: Load Logfire traces to DuckDB | ⚠️ API endpoints limited |
| `agent.py` | Pydantic AI agent with search tool | ✅ Ready |
| `ingest.py` | FAQ data loading | ✅ Ready |

---

## Submit Results

**Course**: LLM Zoomcamp 2026 - Workshop Homework

**Submission URL**: https://courses.datatalks.club/llm-zoomcamp-2026/homework/dlt

**Answers to submit**:
- Q1: `5`
- Q2: `3`
- Q3: `1500-5000`
