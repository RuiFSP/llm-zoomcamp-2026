import marimo

__generated_with = "0.23.9"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Homework 05: Monitoring (marimo)

    This notebook computes Q1-Q6 for Homework 05 using OpenTelemetry tracing.
    """)
    return


@app.cell
def _():
    import json
    import os
    import sqlite3
    from collections import Counter
    from pathlib import Path

    import pandas as pd
    from dotenv import load_dotenv
    from openai import OpenAI
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        SimpleSpanProcessor,
        SpanExporter,
        SpanExportResult,
    )

    from rag_helper import RAGBase
    from starter import index

    homework_dir = Path(__file__).resolve().parent
    repo_root = homework_dir.parents[1]
    traces_db_path = homework_dir / "traces.db"
    load_dotenv(dotenv_path=repo_root / ".env", override=True)
    return (
        Counter,
        OpenAI,
        RAGBase,
        SimpleSpanProcessor,
        SpanExportResult,
        SpanExporter,
        TracerProvider,
        index,
        json,
        os,
        pd,
        sqlite3,
        traces_db_path,
    )


@app.cell
def _(SpanExportResult, SpanExporter, sqlite3):
    class MemorySpanExporter(SpanExporter):
        def __init__(self):
            self.spans = []

        def export(self, spans):
            self.spans.extend(spans)
            return SpanExportResult.SUCCESS

        def get_finished_spans(self):
            return list(self.spans)

        def shutdown(self):
            return

        def force_flush(self, timeout_millis=30000):
            return True

    class SQLiteSpanExporter(SpanExporter):
        def __init__(self, db_path="traces.db"):
            self.conn = sqlite3.connect(db_path)
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS spans (
                    name TEXT,
                    start_time INTEGER,
                    end_time INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost REAL
                )
                """
            )
            self.conn.commit()

        def export(self, spans):
            for span in spans:
                attrs = dict(span.attributes or {})
                self.conn.execute(
                    "INSERT INTO spans VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        span.name,
                        span.start_time,
                        span.end_time,
                        attrs.get("input_tokens"),
                        attrs.get("output_tokens"),
                        attrs.get("cost"),
                    ),
                )
            self.conn.commit()
            return SpanExportResult.SUCCESS

        def shutdown(self):
            self.conn.close()

        def force_flush(self, timeout_millis=30000):
            return True

    return MemorySpanExporter, SQLiteSpanExporter


@app.cell
def _(RAGBase):
    class RAGTraced(RAGBase):
        @staticmethod
        def calculate_cost(model, usage):
            if "gpt-5.4-mini" in model:
                return (usage.input_tokens * 0.15 + usage.output_tokens * 0.60) / 1_000_000
            return 0.0

        def __init__(self, *args, tracer, **kwargs):
            super().__init__(*args, **kwargs)
            self.tracer = tracer

        def search(self, query, num_results=5):
            with self.tracer.start_as_current_span("search"):
                return super().search(query, num_results=num_results)

        def llm(self, prompt):
            with self.tracer.start_as_current_span("llm") as span:
                response = super().llm(prompt)
                usage = response.usage
                span.set_attribute("input_tokens", usage.input_tokens)
                span.set_attribute("output_tokens", usage.output_tokens)
                span.set_attribute("cost", self.calculate_cost(self.model, usage))
                return response

        def rag(self, query):
            with self.tracer.start_as_current_span("rag"):
                search_results = self.search(query)
                prompt = self.build_prompt(query, search_results)
                response = self.llm(prompt)
                return response.output_text

    return (RAGTraced,)


@app.cell
def _(
    Counter,
    MemorySpanExporter,
    OpenAI,
    RAGTraced,
    SQLiteSpanExporter,
    SimpleSpanProcessor,
    TracerProvider,
    index,
    os,
    pd,
    sqlite3,
    traces_db_path,
):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing")

    query = "How does the agentic loop keep calling the model until it stops?"

    if traces_db_path.exists():
        traces_db_path.unlink()

    provider = TracerProvider()
    memory_exporter = MemorySpanExporter()
    sqlite_exporter = SQLiteSpanExporter(str(traces_db_path))
    provider.add_span_processor(SimpleSpanProcessor(memory_exporter))
    provider.add_span_processor(SimpleSpanProcessor(sqlite_exporter))
    tracer = provider.get_tracer("llm-zoomcamp-homework05")

    rag = RAGTraced(index=index, llm_client=OpenAI(), tracer=tracer)

    answer = rag.rag(query)
    spans_once = list(memory_exporter.get_finished_spans())

    for _ in range(3):
        rag.rag(query)

    sqlite_exporter.shutdown()

    llm_once = [s for s in spans_once if s.name == "llm"][0]
    llm_attrs = dict(llm_once.attributes or {})
    llm_duration = [
        (s.end_time - s.start_time) / 1_000_000 for s in spans_once if s.name == "llm"
    ][0]

    conn = sqlite3.connect(str(traces_db_path))
    df = pd.read_sql_query("SELECT * FROM spans", conn)
    conn.close()

    span_names = sorted(df["name"].dropna().unique().tolist())

    df_non_rag = df[df["name"] != "rag"].copy()
    df_non_rag["duration_ms"] = (df_non_rag["end_time"] - df_non_rag["start_time"]) / 1_000_000
    totals = (
        df_non_rag.groupby("name", as_index=False)["duration_ms"]
        .sum()
        .sort_values("duration_ms", ascending=False)
    )

    llm_inputs = df[df["name"] == "llm"]["input_tokens"].dropna().astype(float).tolist()
    vmax = max(llm_inputs)
    vmin = min(llm_inputs)
    variation = 0.0 if vmax == 0 else (vmax - vmin) / vmax

    def q2(v):
        return min([700, 7000, 70000, 700000], key=lambda x: abs(x - v))

    def q3(v):
        if v < 100:
            return "Under 100ms"
        if v < 500:
            return "100-500ms"
        if v < 2000:
            return "500-2000ms"
        return "Over 2000ms"

    def q4(names):
        if names == ["rag"]:
            return "Only rag"
        if names == ["llm", "rag"]:
            return "rag and llm"
        if names == ["llm", "rag", "search"]:
            return "rag, search, and llm"
        return f"Observed: {names}"

    def q6(v):
        if v == 0:
            return "They're identical"
        if v <= 0.10:
            return "Within 10% of each other"
        if v <= 0.50:
            return "Within 50% of each other"
        return "They vary more than 50%"

    out = {
        "query": query,
        "answer_preview": answer[:220],
        "q1": 3,
        "q2": q2(llm_attrs.get("input_tokens")),
        "q3": q3(llm_duration),
        "q4": q4(span_names),
        "q5": totals.iloc[0]["name"] if len(totals) else None,
        "q6": q6(variation),
        "q2_input_tokens": llm_attrs.get("input_tokens"),
        "q3_llm_duration_ms": llm_duration,
        "q6_variation_ratio": variation,
        "span_counts": dict(Counter(df["name"].tolist())),
    }
    return (out,)


@app.cell
def _(json, mo, out):
    mo.md(
        "\n".join(
            [
                "## Final Answers",
                "",
                f"1. Q1: {out['q1']}",
                f"2. Q2: {out['q2']} (measured {out['q2_input_tokens']})",
                f"3. Q3: {out['q3']} (llm {out['q3_llm_duration_ms']:.2f} ms)",
                f"4. Q4: {out['q4']}",
                f"5. Q5: {out['q5']}",
                f"6. Q6: {out['q6']} (variation {out['q6_variation_ratio']:.4f})",
                "",
                "```json",
                json.dumps(out, indent=2),
                "```",
            ]
        )
    )
    return


if __name__ == "__main__":
    app.run()
