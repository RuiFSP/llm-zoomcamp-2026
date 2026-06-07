# llm-zoomcamp-2026

This repository hosts materials and homeworks for the LLM Zoomcamp maintained by RuiFSPinto.

Purpose
- Central place for course modules, class materials, and homework assignments.
- Each module lives in a top-level folder named `NN-topic-name` and contains the module's `class_materials/` and `homeworkNN/` directories.

Reference
- This roadmap and structure are inspired by the DataTalksClub LLM Zoomcamp: https://github.com/DataTalksClub/llm-zoomcamp

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

Proposed module roadmap
1. 01-intro — Course intro, environment, datasets, basic prompts
2. 02-foundations — LLM basics, tokens, prompting, evaluation
3. 03-retrieval-augmented-generation — Inverted index, FAISS, embeddings, RAG
4. 04-agents — Tools, function calling, simple agent loops
5. 05-agentic-rag — Combining agents with RAG for pipelines (current: `01-agentic-rag`)
6. 06-evaluation-and-debugging — Metrics, adversarial testing, prompt-debugging
7. 07-deployment-and-costs — Serving models, latency, cost optimization
8. 08-advanced-topics — Multimodality, fine-tuning, RLHF overview

Contributing
- When adding content, follow the module structure and add a short summary in the module folder `README.md`.
- Optionally open an OpenSpec change to track larger scope changes (I can help create one).

Contact
- Maintainer: RuiFSPinto

Files added
- `syllabus.md` — local course schedule and roadmap.
- `docs/datatalksclub-mapping.md` — mapping to DataTalksClub syllabus.
