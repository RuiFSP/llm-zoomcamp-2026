# Module 01 — Agentic RAG (summary)

This module covers building a Retrieval-Augmented Generation (RAG) system and
making it agentic. The goal is practical: take plain course lesson pages as
knowledge, index them, and use an LLM to answer questions using retrieved
context.

Key topics covered

- RAG fundamentals: combining a retriever (search/index) with an LLM to answer
  queries using retrieved context instead of relying only on the model's
  parametric knowledge.
- Document ingestion: fetching lesson markdown files from GitHub with
  `gitsource` and parsing into simple documents with `filename` and
  `content` fields.
- Indexing and search: using `minsearch` to index `content` as a text field
  and `filename` as a keyword field; crafting queries and inspecting top
  results to validate relevance.
- Chunking for better retrieval: splitting long pages into overlapping
  chunks (`chunk_documents`) so matches are more precise and prompts remain
  smaller.
- Token usage and cost awareness: estimating prompt tokens with `tiktoken`
  when available (fallback heuristic otherwise), reading provider-reported
  usage from LLM responses, and computing approximate cost per token.
- Making RAG robust: adapting helper classes to work with `filename`/`content`
  documents, handling different index APIs, and defensively extracting
  provider usage fields.
- Agentic loop: giving the model a `search` tool (implemented over the chunk
  index) and running an agent loop (ToyAIKit or equivalent) that decides when
  to call `search` and when to answer; observing that tool-call counts vary
  between runs.

What this module emphasizes (no solutions shown)

- Practical end-to-end engineering: ingest → index → retrieve → prompt →
  call LLM. The exercises reinforce how small engineering choices (index
  schema, chunk size, prompt structure) affect retrieval quality and token
  footprint.
- Measurement and defensiveness: always verify provider usage, gracefully
  handle missing packages (e.g., `tiktoken`), and prefer conservative
  fallbacks in production-like helpers.
- Reproducibility: pin commits when fetching external data and include
  small scripts (or notebooks) to reproduce experiments.

Files of interest

- `homework01/` — contains the module homework notebook and supporting
  helper code used for the exercises (indexing, RAG helper, chunking, and an
  agent cell). This folder intentionally does not include answer dumps in the
  README — the notebook and script show how to reproduce the measurements.

Next steps

- If you want, I can add a short `README` section showing how to run the
  reproducibility script (`homework01/answer_homework.py`) and a small test
  harness under `homework01/tests/` to automate answer checks.
