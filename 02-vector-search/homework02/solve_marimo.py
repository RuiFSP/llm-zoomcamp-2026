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
    # Homework 02: Vector Search

    In this notebook we solve all 6 questions from homework 2 using vector search,
    keyword search, and hybrid search with Reciprocal Rank Fusion (RRF).
    """)
    return


@app.cell
def _(mo):
    import sys
    import os

    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

    import numpy as np
    from tqdm.auto import tqdm
    from gitsource import GithubRepositoryDataReader, chunk_documents
    from minsearch import VectorSearch, Index
    from embedder import Embedder

    embed = Embedder()
    mo.md(
        f"✅ Embedder loaded (model: `all-MiniLM-L6-v2`, dim={embed.encode('test').shape[0]})"
    )
    return (
        GithubRepositoryDataReader,
        Index,
        VectorSearch,
        chunk_documents,
        embed,
        np,
        tqdm,
    )


@app.cell
def _(GithubRepositoryDataReader, mo):
    reader = GithubRepositoryDataReader(
        repo_owner="DataTalksClub",
        repo_name="llm-zoomcamp",
        commit_id="8c1834d",
        allowed_extensions={"md"},
        filename_filter=lambda path: "/lessons/" in path,
    )
    documents = [file.parse() for file in reader.read()]
    mo.md(f"✅ Loaded **{len(documents)}** lesson pages from GitHub (commit `8c1834d`)")
    return (documents,)


@app.cell
def _(embed, mo):
    q1_query = "How does approximate nearest neighbor search work?"
    v_q1 = embed.encode(q1_query)
    v0 = float(v_q1[0])

    _q1_opts = {"-0.31": -0.31, "-0.02": -0.02, "0.12": 0.12, "0.44": 0.44}
    _q1_ans = min(_q1_opts, key=lambda k: abs(_q1_opts[k] - v0))

    mo.md(
        f"""
        ## Q1. Embedding a query

        **Query:** _{q1_query}_

        **`v[0]` = {v0:.4f}** → closest option: **{_q1_ans}**
        """
    )
    return (v_q1,)


@app.cell
def _(documents, embed, mo, v_q1):
    q2_page = "02-vector-search/lessons/07-sqlitesearch-vector.md"
    q2_doc = next(d for d in documents if d["filename"] == q2_page)
    v_q2 = embed.encode(q2_doc["content"])
    cos_sim = float(v_q1.dot(v_q2))

    _q2_opts = {0.07: 0.07, 0.37: 0.37, 0.68: 0.68, 0.92: 0.92}
    _q2_ans = min(_q2_opts, key=lambda k: abs(k - cos_sim))

    mo.md(
        f"""
        ## Q2. Cosine similarity

        **Page:** `{q2_page}`

        **Cosine similarity:** **{cos_sim:.4f}** → closest option: **{_q2_ans}**
        """
    )
    return


@app.cell
def _(chunk_documents, documents, embed, mo, np, tqdm, v_q1):
    chunks = chunk_documents(documents, size=2000, step=1000)

    X_list = []
    for i in tqdm(range(0, len(chunks), 50), desc="Embedding chunks"):
        batch = [c["content"] for c in chunks[i : i + 50]]
        vecs = embed.encode_batch(batch)
        X_list.append(vecs)
    X = np.vstack(X_list)

    scores = X.dot(v_q1)
    best_idx = int(np.argmax(scores))
    best_chunk = chunks[best_idx]

    mo.md(
        f"""
        ## Q3. Chunking and search by hand

        Created **{len(chunks)}** chunks (size=2000, step=1000).

        Best chunk score: **{scores[best_idx]:.4f}**

        **Answer:** `{best_chunk["filename"]}`
        """
    )
    return X, chunks


@app.cell
def _(VectorSearch, X, chunks, embed, mo):
    vindex = VectorSearch()
    vindex.fit(X, chunks)

    q4_query = "What metric do we use to evaluate a search engine?"
    v_q4 = embed.encode(q4_query)
    q4_results = vindex.search(v_q4, num_results=5)

    mo.md(
        f"""
        ## Q4. Vector search with minsearch

        **Query:** _{q4_query}_

        | Rank | Filename |
        |------|----------|
        """
        + "\n".join(
            f"| {i+1} | `{r['filename']}` |" for i, r in enumerate(q4_results)
        )
        + f"\n\n**Answer:** `{q4_results[0]['filename']}`"
    )
    return (vindex,)


@app.cell
def _(Index, chunks, embed, mo, vindex):
    text_index = Index(text_fields=["content"])
    text_index.fit(chunks)

    q5_query = "How do I store vectors in PostgreSQL?"
    v_q5 = embed.encode(q5_query)

    vector_results_q5 = vindex.search(v_q5, num_results=5)
    text_results_q5 = text_index.search(q5_query, num_results=5)

    vector_fns = {r["filename"] for r in vector_results_q5}
    text_fns = {r["filename"] for r in text_results_q5}
    only_vector = vector_fns - text_fns

    mo.md(
        f"""
        ## Q5. Text search vs vector search

        **Query:** _{q5_query}_

        **Vector top 5:**
        """
        + "\n".join(f"  {i+1}. `{r['filename']}`" for i, r in enumerate(vector_results_q5))
        + "\n\n**Text top 5:**\n"
        + "\n".join(f"  {i+1}. `{r['filename']}`" for i, r in enumerate(text_results_q5))
        + (
            f"\n\n✅ **Answer:** `{list(only_vector)[0]}` appears in vector results but **not** in text results"
            if only_vector
            else "\n\nNo difference found"
        )
    )
    return (text_index,)


@app.cell
def _(embed, mo, text_index, vindex):
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

    q6_query = "How do I give the model access to tools?"
    v_q6 = embed.encode(q6_query)

    vector_results_q6 = vindex.search(v_q6, num_results=10)
    text_results_q6 = text_index.search(q6_query, num_results=10)

    hybrid_results = rrf([vector_results_q6, text_results_q6], k=60)

    mo.md(
        f"""
        ## Q6. Hybrid search (RRF)

        **Query:** _{q6_query}_

        | Rank | Source | Filename |
        |------|--------|----------|
        """
        + "\n".join(
            f"| {i+1} | Hybrid | `{r['filename']}` |"
            for i, r in enumerate(hybrid_results)
        )
        + f"\n\n**Answer:** `{hybrid_results[0]['filename']}`"
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Summary of Answers

    | Question | Answer |
    |---|---|
    | **Q1** | `-0.02` |
    | **Q2** | `0.37` |
    | **Q3** | `02-vector-search/lessons/07-sqlitesearch-vector.md` |
    | **Q4** | `04-evaluation/lessons/05-search-metrics.md` |
    | **Q5** | `02-vector-search/lessons/08-pgvector.md` |
    | **Q6** | `01-agentic-rag/lessons/13-function-calling.md` |
    """)
    return


if __name__ == "__main__":
    app.run()
