# Homework 05 Solutions - Monitoring with OpenTelemetry

This folder follows the same structure as previous solved modules:

- `solve_marimo.py`: reproducible marimo notebook-style solver
- `homework05_solution.md`: final selected answers and short evidence notes

## How to Run

1. Ensure dependencies are available:

```bash
uv add opentelemetry-api opentelemetry-sdk
```

2. Add `OPENAI_API_KEY` to `.env`.

3. Run marimo app:

```bash
uv run marimo run 05-monitoring/homework05/solve_marimo.py
```

4. Copy computed values from the app output into the answer block below.

## Final Answers

1. Q1: `3`
2. Q2: `7000` (measured input tokens: `7111`)
3. Q3: `Over 2000ms` (measured llm span: `4033.05 ms`)
4. Q4: `rag, search, and llm`
5. Q5: `llm`
6. Q6: `They're identical`

## Evidence Notes

- Query used:
  - `How does the agentic loop keep calling the model until it stops?`
- Tracing design:
  - `RAGTraced` wraps `rag`, `search`, and `llm` each in their own span
  - `llm` span records `input_tokens`, `output_tokens`, `cost`
- Persistence:
  - `SQLiteSpanExporter` writes spans to `traces.db`
- Stability check:
  - Total of 4 calls with same query and comparison of `input_tokens`

### Run Output Snapshot

- `q1_span_count`: `3`
- `q2_input_tokens`: `7111`
- `q2_output_tokens`: `99`
- `q3_all_durations_ms`:
  - `search`: `142.66`
  - `llm`: `4033.05`
  - `rag`: `4649.66`
- `q4_span_names`: `['llm', 'rag', 'search']`
- `q5_total_duration_by_span_ms` (excluding rag):
  - `search`: `147.26`
  - `llm`: `8396.73`
- `q6_llm_input_tokens`: `[7111, 7111, 7111, 7111]`
- `q6_variation_ratio`: `0.0`
