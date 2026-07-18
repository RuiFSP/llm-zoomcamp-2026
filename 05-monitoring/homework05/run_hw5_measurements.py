import json
import os
import sqlite3
from collections import Counter
from pathlib import Path

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


load_dotenv(dotenv_path=Path("../../.env").resolve(), override=True)

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit("OPENAI_API_KEY missing in environment or .env")


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


def map_q2_option(input_tokens):
    options = [700, 7000, 70000, 700000]
    return min(options, key=lambda x: abs(x - input_tokens))


def map_q3_option(duration_ms):
    if duration_ms < 100:
        return "Under 100ms"
    if duration_ms < 500:
        return "100-500ms"
    if duration_ms < 2000:
        return "500-2000ms"
    return "Over 2000ms"


def map_q4_option(span_names):
    if span_names == ["rag"]:
        return "Only rag"
    if span_names == ["llm", "rag"]:
        return "rag and llm"
    if span_names == ["llm", "rag", "search"]:
        return "rag, search, and llm"
    return f"Observed: {span_names}"


def map_q6_option(var_ratio):
    if var_ratio == 0:
        return "They're identical"
    if var_ratio <= 0.10:
        return "Within 10% of each other"
    if var_ratio <= 0.50:
        return "Within 50% of each other"
    return "They vary more than 50%"


def main():
    query = "How does the agentic loop keep calling the model until it stops?"

    db_path = Path("traces.db")
    if db_path.exists():
        db_path.unlink()

    provider = TracerProvider()
    memory_exporter = MemorySpanExporter()
    sqlite_exporter = SQLiteSpanExporter(str(db_path))
    provider.add_span_processor(SimpleSpanProcessor(memory_exporter))
    provider.add_span_processor(SimpleSpanProcessor(sqlite_exporter))
    tracer = provider.get_tracer("llm-zoomcamp-homework05")

    rag = RAGTraced(index=index, llm_client=OpenAI(), tracer=tracer)

    answer = rag.rag(query)
    spans_once = list(memory_exporter.get_finished_spans())
    for _ in range(3):
        rag.rag(query)

    sqlite_exporter.shutdown()

    q1 = len(spans_once)
    llm_once = [s for s in spans_once if s.name == "llm"][0]
    llm_attrs = dict(llm_once.attributes or {})
    q2_input = llm_attrs.get("input_tokens")
    q2_output = llm_attrs.get("output_tokens")

    durations = []
    for s in spans_once:
        ms = (s.end_time - s.start_time) / 1_000_000
        durations.append((s.name, ms))
    llm_duration = [ms for n, ms in durations if n == "llm"][0]

    conn = sqlite3.connect(str(db_path))
    rows = conn.execute(
        "SELECT name, start_time, end_time, input_tokens, output_tokens, cost FROM spans"
    ).fetchall()
    conn.close()

    names = sorted({r[0] for r in rows})
    totals = {}
    for name, st, et, *_ in rows:
        if name == "rag":
            continue
        totals[name] = totals.get(name, 0.0) + (et - st) / 1_000_000
    q5 = max(totals, key=totals.get) if totals else None

    llm_inputs = [r[3] for r in rows if r[0] == "llm" and r[3] is not None]
    vmax = max(llm_inputs)
    vmin = min(llm_inputs)
    var_ratio = 0.0 if vmax == 0 else (vmax - vmin) / vmax

    out = {
        "query": query,
        "answer_preview": answer[:240],
        "q1_span_count": q1,
        "q2_input_tokens": q2_input,
        "q2_output_tokens": q2_output,
        "q2_choice": map_q2_option(q2_input),
        "q3_llm_duration_ms": llm_duration,
        "q3_choice": map_q3_option(llm_duration),
        "q3_all_durations_ms": durations,
        "q4_span_names": names,
        "q4_choice": map_q4_option(names),
        "q5_total_duration_by_span_ms": totals,
        "q5_choice": q5,
        "q6_llm_input_tokens": llm_inputs,
        "q6_variation_ratio": var_ratio,
        "q6_choice": map_q6_option(var_ratio),
        "span_counts": dict(Counter([r[0] for r in rows])),
        "total_spans_saved": len(rows),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
