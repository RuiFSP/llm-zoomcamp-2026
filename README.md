# llm-zoomcamp-2026

This repository hosts materials and homeworks for the LLM Zoomcamp maintained by RuiFSPinto.

Purpose
- Central place for course modules, class materials, and homework assignments.
- Each module lives in a top-level folder named `NN-topic-name` and contains the module's `class_materials/` and `homeworkNN/` directories.

Reference
- The structure is inspired by the DataTalksClub LLM Zoomcamp: https://github.com/DataTalksClub/llm-zoomcamp

Module structure (convention)
- `01-intro/`
	- `class_materials/` (slides, notebooks, code)
	- `homework01/` (assignments and tests)

How to add and maintain a module
1. Create a new folder `NN-topic-name/` following numbering order.
2. Each week add the current lesson assets to `class_materials/` and the week's assignments to `homeworkNN/`.
	- `class_materials/` should contain lesson markdown, notebooks, slides, and runnable code.
	- `homeworkNN/` should contain the assignment, tests (where applicable), and submission instructions.
3. Update this README's roadmap when you add or reorder modules.


## Module Summaries

- **01-agentic-rag — Agentic RAG:** Build a Retrieval-Augmented Generation
	(RAG) pipeline from lesson pages: ingest lesson markdowns from GitHub,
	index content with `minsearch`, apply chunking for long pages, and combine
	retrieval with an LLM to answer questions. The module additionally covers
	measuring token usage and costs, and turning RAG into an agent by exposing
	a `search` tool so the model can decide when to look up information.

	- Folder: [01-agentic-rag](01-agentic-rag)

- **02-vector-search — Vector Search (materials available):** Covers
  embeddings, vector indexes (pgvector, SQLite vector extensions), persistent
  vector stores, and practical examples with `minsearch` + vector backends.
  Folder: [02-vector-search](02-vector-search)