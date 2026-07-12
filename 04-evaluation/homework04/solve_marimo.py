import marimo

__generated_with = "0.23.9"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # Homework 04: Evaluation (marimo)

    This notebook reproduces Homework 04 end-to-end:

    - Q1: average input tokens for 3 generated-question calls
    - Q2/Q3: first result for text and vector search
    - Q4/Q5: Hit Rate and MRR evaluation
    - Q6: hybrid tuning with RRF (`k in [1, 50, 100, 200]`)

    It uses the same dataset and commit from the homework statement.
    """)
    return


@app.cell
def _(mo):
    import os
    import sys
    import json
    from pathlib import Path

    import numpy as np
    import pandas as pd
    from dotenv import load_dotenv
    from gitsource import GithubRepositoryDataReader, chunk_documents
    from minsearch import Index, VectorSearch

    # Resolve stable paths from this file location.
    homework_dir = Path(__file__).resolve().parent
    repo_root = homework_dir.parents[1]

    # Use local homework embedder copy to avoid cross-folder import issues.
    sys.path.insert(0, str(homework_dir))
    from embedder import Embedder

    load_dotenv(dotenv_path=repo_root / ".env", override=False)

    mo.md(f"✅ Imports and environment ready (repo root: {repo_root})")
    return (
        Embedder,
        GithubRepositoryDataReader,
        Index,
        VectorSearch,
        chunk_documents,
        homework_dir,
        json,
        np,
        os,
        pd,
        repo_root,
    )


@app.cell
def _(GithubRepositoryDataReader, chunk_documents, homework_dir, mo, pd):
    reader = GithubRepositoryDataReader(
        repo_owner="DataTalksClub",
        repo_name="llm-zoomcamp",
        commit_id="8c1834d",
        allowed_extensions={"md"},
        filename_filter=lambda path: "/lessons/" in path,
    )
    documents = [file.parse() for file in reader.read()]

    gt_path = homework_dir / "ground-truth.csv"
    df_gt = pd.read_csv(gt_path)
    ground_truth = df_gt.to_dict(orient="records")

    chunks = chunk_documents(documents, size=2000, step=1000)

    mo.md(
        f"""
    ✅ Loaded **{len(documents)}** lesson pages  
    ✅ Loaded **{len(ground_truth)}** ground-truth questions  
    ✅ Created **{len(chunks)}** chunks (`size=2000`, `step=1000`)
    """
    )
    return chunks, documents, ground_truth


@app.cell
def _(Embedder, Index, VectorSearch, chunks, mo, np, repo_root):
    text_index = Index(text_fields=["content"], keyword_fields=["filename"])
    text_index.fit(chunks)

    def text_search(query, num_results=5):
        return text_index.search(query, num_results=num_results)

    embed = Embedder(path=repo_root / "models/Xenova/all-MiniLM-L6-v2")

    X_batches = []
    for i in range(0, len(chunks), 64):
        batch = [c["content"] for c in chunks[i : i + 64]]
        X_batches.append(embed.encode_batch(batch))
    X = np.vstack(X_batches)

    vector_index = VectorSearch()
    vector_index.fit(X, chunks)

    def vector_search(query, num_results=5):
        return vector_index.search(embed.encode(query), num_results=num_results)

    def rrf(result_lists, k=60, num_results=5):
        scores = {}
        docs = {}

        for results in result_lists:
            for rank, doc in enumerate(results):
                key = (doc["filename"], doc["start"])
                scores[key] = scores.get(key, 0) + 1 / (k + rank)
                docs[key] = doc

        ranked = sorted(scores, key=scores.get, reverse=True)
        return [docs[key] for key in ranked[:num_results]]

    def hybrid_search(query, k=60):
        text_results = text_search(query, num_results=10)
        vector_results = vector_search(query, num_results=10)
        return rrf([text_results, vector_results], k=k)

    mo.md("✅ Text, vector, and hybrid search functions are ready")
    return hybrid_search, text_search, vector_search


@app.cell
def _(ground_truth, hybrid_search, text_search, vector_search):
    def compute_relevance(q, search_function):
        target = q["filename"]
        results = search_function(query=q["question"])
        return [int(d["filename"] == target) for d in results]

    def compute_relevance_total(gt, search_function):
        return [compute_relevance(q, search_function) for q in gt]

    def hit_rate(relevance):
        return sum(1 for row in relevance if 1 in row) / len(relevance)

    def mrr(relevance):
        total = 0.0
        for row in relevance:
            for rank, val in enumerate(row, start=1):
                if val == 1:
                    total += 1 / rank
                    break
        return total / len(relevance)

    def evaluate(gt, search_function):
        rel = compute_relevance_total(gt, search_function)
        return {"hit_rate": hit_rate(rel), "mrr": mrr(rel)}

    first_question = ground_truth[0]["question"]

    q2_first_text_filename = text_search(first_question, num_results=5)[0]["filename"]
    q3_first_vector_filename = vector_search(first_question, num_results=5)[0]["filename"]

    q4_text_eval = evaluate(ground_truth, text_search)
    q5_vector_eval = evaluate(ground_truth, vector_search)

    q6_hybrid_by_k = {}
    for k in [1, 50, 100, 200]:
        q6_hybrid_by_k[k] = evaluate(
            ground_truth,
            lambda query, k=k: hybrid_search(query, k=k),
        )
    return (
        q2_first_text_filename,
        q3_first_vector_filename,
        q4_text_eval,
        q5_vector_eval,
        q6_hybrid_by_k,
    )


@app.cell
def _(documents, json, os):
    q1 = {
        "status": "skipped",
        "input_tokens": [],
        "average_input_tokens": None,
        "error": None,
    }

    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        try:
            from pydantic import BaseModel
            from openai import OpenAI

            class Questions(BaseModel):
                questions: list[str]

            data_gen_instructions = """
    You emulate a student who is taking our LLM course.
    You are given one lesson page from the course.
    Formulate 5 questions this student might ask that are answered by this page.

    Rules:
    - The page should contain the answer to each question.
    - Make the questions complete and not too short.
    - Use as few words as possible from the page; don't copy its phrasing.
    - The questions should resemble how people actually ask things online:
      not too formal, not too short, not too long.
    - Ask about the content of the lesson, not about its formatting or filename.
    """.strip()

            wanted = [
                "01-agentic-rag/lessons/01-intro.md",
                "01-agentic-rag/lessons/02-environment.md",
                "01-agentic-rag/lessons/03-rag.md",
            ]

            by_name = {d["filename"]: d for d in documents}
            client = OpenAI(api_key=api_key)

            usages = []
            for fn in wanted:
                doc = by_name[fn]
                user_prompt = json.dumps(
                    {"filename": doc["filename"], "content": doc["content"]}
                )

                response = client.responses.parse(
                    model="gpt-5.4-mini",
                    input=[
                        {"role": "developer", "content": data_gen_instructions},
                        {"role": "user", "content": user_prompt},
                    ],
                    text_format=Questions,
                )

                usage = response.usage
                inp = getattr(usage, "input_tokens", None)
                if inp is None:
                    inp = getattr(usage, "prompt_tokens", None)
                usages.append(inp)

            q1 = {
                "status": "ok",
                "input_tokens": usages,
                "average_input_tokens": sum(usages) / len(usages),
                "error": None,
            }
        except Exception as e:
            q1 = {
                "status": "error",
                "input_tokens": [],
                "average_input_tokens": None,
                "error": str(e),
            }
    return (q1,)


@app.cell
def _(
    mo,
    q1,
    q2_first_text_filename,
    q3_first_vector_filename,
    q4_text_eval,
    q5_vector_eval,
    q6_hybrid_by_k,
):
    def closest_option(value, options):
        return min(options, key=lambda x: abs(x - value))

    q1_choice = None
    if q1["average_input_tokens"] is not None:
        q1_choice = closest_option(q1["average_input_tokens"], [140, 1400, 14000, 140000])

    q4_choice = closest_option(q4_text_eval["hit_rate"], [0.55, 0.66, 0.76, 0.88])
    q5_choice = closest_option(q5_vector_eval["mrr"], [0.35, 0.45, 0.55, 0.65])

    best_k = min(
        q6_hybrid_by_k.keys(),
        key=lambda k: (-q6_hybrid_by_k[k]["mrr"], k),
    )

    q1_details = "Not computed (missing key or API error)."
    if q1["status"] == "ok":
        q1_details = (
            f"input_tokens={q1['input_tokens']}, avg={q1['average_input_tokens']:.1f}, "
            f"closest option={q1_choice}"
        )
    elif q1["status"] == "error":
        q1_details = f"Error while calling API: {q1['error']}"

    summary = [
        f"- Q1: {q1_choice if q1_choice is not None else 'N/A'} ({q1_details})",
        f"- Q2: {q2_first_text_filename}",
        f"- Q3: {q3_first_vector_filename}",
        f"- Q4: {q4_choice} (measured hit_rate={q4_text_eval['hit_rate']:.4f})",
        f"- Q5: {q5_choice} (measured mrr={q5_vector_eval['mrr']:.4f})",
        f"- Q6: {best_k} (best MRR among k=1,50,100,200)",
    ]

    k_rows = "\n".join(
        [
            f"| {k} | {q6_hybrid_by_k[k]['hit_rate']:.4f} | {q6_hybrid_by_k[k]['mrr']:.4f} |"
            for k in [1, 50, 100, 200]
        ]
    )

    mo.md(
        "\n".join(
            [
                "## Results",
                "",
                *summary,
                "",
                "### Hybrid Metrics by k",
                "",
                "| k | Hit Rate | MRR |",
                "|---|---:|---:|",
                k_rows,
            ]
        )
    )
    return best_k, q1_choice, q4_choice, q5_choice


@app.cell
def _(
    best_k,
    mo,
    q1_choice,
    q2_first_text_filename,
    q3_first_vector_filename,
    q4_choice,
    q5_choice,
):
    mo.md(
        "\n".join(
            [
                "## Final Answers",
                "",
                f"1. Q1: {q1_choice if q1_choice is not None else 'N/A'}",
                f"2. Q2: {q2_first_text_filename}",
                f"3. Q3: {q3_first_vector_filename}",
                f"4. Q4: {q4_choice}",
                f"5. Q5: {q5_choice}",
                f"6. Q6: {best_k}",
            ]
        )
    )
    return


if __name__ == "__main__":
    app.run()
