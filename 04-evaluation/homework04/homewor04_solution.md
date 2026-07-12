# Homework 04 Solutions - Evaluation

## Execution Summary

All results were computed from the homework dataset and retrieval pipeline:

- Repository source: DataTalksClub/llm-zoomcamp
- Commit: 8c1834d
- Lesson pages loaded: 72
- Chunks created (size=2000, step=1000): 295
- Ground truth rows: 360
- LLM for Q1 generation: gpt-5.4-mini

Measured values used for answers:

| Item | Measured Value |
|---|---|
| Q1 input tokens (3 calls) | [1021, 1287, 1754] |
| Q1 average input tokens | **1354.0** |
| Q2 top-1 filename (text search) | **01-agentic-rag/lessons/03-rag.md** |
| Q3 top-1 filename (vector search) | **01-agentic-rag/lessons/01-intro.md** |
| Q4 text search hit rate | **0.7583** |
| Q5 vector search MRR | **0.5486** |
| Q6 hybrid MRR @ k=1 | **0.6482** |
| Q6 hybrid MRR @ k=50 | 0.6379 |
| Q6 hybrid MRR @ k=100 | 0.6379 |
| Q6 hybrid MRR @ k=200 | 0.6379 |

---

## Question 1: Generating Questions

**Question:** What's the average number of input tokens across the 3 calls?

**Measured:** 1354.0 average input tokens.

**Selected option:** **1400**

**Why:** 1354 is closest to 1400 among the available options (140, 1400, 14000, 140000).

---

## Question 2: First Result with Text Search

**Question:** After running text search for the first ground-truth question, what is the first filename?

**Measured top result:** 01-agentic-rag/lessons/03-rag.md

**Selected option:** **01-agentic-rag/lessons/03-rag.md**

**Why:** It is exactly the top-1 returned by text search.

---

## Question 3: First Result with Vector Search

**Question:** After running vector search for the same first question, what is the first filename?

**Measured top result:** 01-agentic-rag/lessons/01-intro.md

**Selected option:** **01-agentic-rag/lessons/01-intro.md**

**Why:** It is exactly the top-1 returned by vector search.

---

## Question 4: Evaluating Text Search

**Question:** What's the Hit Rate for text search?

**Measured hit rate:** 0.7583

**Selected option:** **0.76**

**Why:** 0.7583 rounds to and is closest to 0.76.

---

## Question 5: Evaluating Vector Search

**Question:** What's the MRR for vector search?

**Measured MRR:** 0.5486

**Selected option:** **0.55**

**Why:** 0.5486 rounds to and is closest to 0.55.

---

## Question 6: Tuning Hybrid Search

**Question:** Which k gives the best MRR among 1, 50, 100, 200?

**Measured MRR by k:**
- k=1: 0.6482
- k=50: 0.6379
- k=100: 0.6379
- k=200: 0.6379

**Selected option:** **1**

**Why:** k=1 has the highest MRR. No tie at the top.

---

## Final Answers for Submission

1. Q1: **1400**
2. Q2: **01-agentic-rag/lessons/03-rag.md**
3. Q3: **01-agentic-rag/lessons/01-intro.md**
4. Q4: **0.76**
5. Q5: **0.55**
6. Q6: **1**
