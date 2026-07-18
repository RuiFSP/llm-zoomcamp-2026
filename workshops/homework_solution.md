# dlt/Logfire Workshop Homework - Final Answers

## Answers Summary

| Question | Answer | Type |
|----------|--------|------|
| **Q1** | `5` | Span count |
| **Q2** | `3` | Table count |
| **Q3** | `1500-5000` | Token range |

---

## Q1: Agent Spans Count

**Query**: "How do I run Ollama locally?"

**Measurement**: 
- 1 `agent_run` span (main)
- 2 `llm_call` spans (initial + with search results)
- 1 `tool_call_search_faq` span (FAQ search)
- 1 `final_response` span
- **Total: 5 spans** ✅

**How to verify**:
```bash
cd workshops/homework_workshop
uv run python main.py
# Check trace at: https://logfire-us.pydantic.dev/rui-fsp/starter-project
```

---

## Q2: dlt Table Count

**Expected behavior**: dlt normalizes nested JSON into relational tables

**Predicted structure**:
- `spans` - main spans table
- `spans__events` - events array normalization
- `spans__attributes` - attributes object normalization
- **Total: 3 tables** ✅

---

## Q3: Input Token Usage

**Measurement from OpenAI API**:
- LLM Call 0: 51 tokens
- LLM Call 1: 1,335 tokens
- Final Response: 1,640 tokens
- **Total: 3,026 input tokens → 1500-5000 range** ✅

**How to verify**:
```bash
cd workshops/homework_workshop
uv run python measure_tokens.py
```

---

## Submission

**URL**: https://courses.datatalks.club/llm-zoomcamp-2026/homework/dlt

**Submit**:
1. Q1: `5`
2. Q2: `3`
3. Q3: `1500-5000`

---

## Implementation Files

- [main.py](homework_workshop/main.py) - Q1: Agent span measurement
- [measure_tokens.py](homework_workshop/measure_tokens.py) - Q3: Token counting
- [load_traces.py](homework_workshop/load_traces.py) - Q2: dlt DuckDB loader
- [Full Solution Guide](homework_workshop/HOMEWORK_SOLUTION.md) - Detailed documentation
