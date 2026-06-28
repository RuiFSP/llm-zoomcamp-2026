# llm-zoomcamp-2026

This repository hosts materials and homeworks for the LLM Zoomcamp maintained by RuiFSPinto.

Purpose
- Central place for course modules, class materials, and homework assignments.
- Each module lives in a top-level folder named `NN-topic-name` and contains the module's `class_materials/` and `homeworkNN/` directories.

Reference
- The structure is inspired by the DataTalksClub LLM Zoomcamp: https://github.com/DataTalksClub/llm-zoomcamp


## Course Progress / Module Roadmap

1. 01-agentic-rag — Agentic RAG ([01-agentic-rag](01-agentic-rag)) ✅
2. 02-vector-search — Vector Search ([02-vector-search](02-vector-search)) ✅
3. 03-orchestration — Orchestration (planned)
4. 04-evaluation — Evaluation (planned)
5. 05-monitoring — Monitoring (planned)
6. 06-best-practices — Best Practices (planned)
7. 07-project-example — Project Example (planned)


## Module Summaries

- ### 01-agentic-rag — Agentic RAG:

	![Module 01 infographic](assets/module01_infographic.png)

	#### Key topics covered (Module 01) ✔

	- RAG fundamentals: combining a retriever (index/search) with an LLM to answer
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


- ### 02-vector-search — Vector Search:

	![Module 02 infographic](assets/module02_infographic.png)

	#### Key topics covered (Module 02) ✔

	- Text embeddings: turning text into 384-dimensional vectors using
		`all-MiniLM-L6-v2` via sentence-transformers and ONNX Runtime;
		normalized vectors where dot product equals cosine similarity.
	- Vector search from scratch: embedding all documents into a matrix,
		scoring with numpy dot product, and retrieving top-K via `np.argmax`
		and `np.argsort`.
	- Vector search with minsearch: using `VectorSearch` (same fit/search
		API as text `Index`) with keyword filtering via `filter_dict`.
	- Persistent vector indexes: exploring sqlitesearch (ANN modes:
		LSH/IVF/HNSW) and PGVector for production-grade persistent storage.
	- Lighter deployments with ONNX: replacing the 4.8 GB sentence-transformers
		environment with a 147 MB ONNX Runtime setup — same embeddings,
		33× smaller footprint.
	- Text search vs vector search: comparing keyword (exact match) and
		semantic (embedding similarity) search; observing which pages each
		method surfaces for the same query.
	- Hybrid search with Reciprocal Rank Fusion (RRF): combining ranked lists
		from both methods using `RRF(d) = Σ 1/(k + rank(d))` with k=60 to get
		the best of both approaches.

