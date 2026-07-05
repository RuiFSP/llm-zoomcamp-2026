# Homework 03 Solutions - AI Orchestration with Kestra

## Execution Summary - Token Usage Data

All flows tested with Gemini 2.5-flash model.

| Flow | Configuration | Task | Output Tokens | Execution ID |
|------|--------------|------|---------------|--------------|
| 4 | short summary | multilingual_agent | **102** | 5ubvej6XibRokXLwP95MFA |
| 4 | short summary | english_brevity | 38 | 5ubvej6XibRokXLwP95MFA |
| 4 | long summary | multilingual_agent | 128 | 4hxO2RlMLhaWzPpMLHybTJ |
| 4 | long summary | english_brevity (1 sentence) | 49 | 4hxO2RlMLhaWzPpMLHybTJ |
| 4 | long summary | english_brevity (3 sentences) | 69 | 2B8MWugXBBdzvmJMifbuUP |

---

**Question:** What is the primary reason AI Copilot generates better Kestra flows?

**Answer:** **AI Copilot has access to current Kestra plugin documentation**

**Reasoning:** 
- AI Copilot uses Retrieval Augmented Generation (RAG) to access current Kestra documentation
- This gives it up-to-date information about available plugins, their parameters, and best practices
- In contrast, ChatGPT relies only on training data which may be outdated or incomplete
- RAG provides the model with real-time context about Kestra's capabilities

---

## Question 2: RAG vs No RAG

**Question:** The non-RAG response about Kestra 1.1 features is best described as:

**Answer:** **Vague, generic, or fabricated — the model guesses from training data**

**Evidence from execution:**
- **Flow 1 (without RAG)** - The model relies only on its training data to answer questions about Kestra 1.1
- **Flow 2 (with RAG)** - The model retrieves actual release notes and provides accurate, specific information

**Key insight:** 
- Without context grounding (RAG), LLMs produce hallucinations or generic answers
- With RAG, the same model produces accurate, detailed responses backed by real documentation

---

## Question 3: Token Usage - Short Summary

**Question:** What is the approximate output token count for `multilingual_agent` with `summary_length = short`?

**Answer:** **60-100 tokens** ✓

**Measured Value:** 102 output tokens (slightly above the range, but closest match)

**Execution ID:** 5ubvej6XibRokXLwP95MFA

**Details:**
- multilingual_agent output tokens: **102**
- english_brevity output tokens: 38

---

## Question 4: Token Usage - Long Summary

**Question:** Roughly how many times more output tokens does the long summary use?

**Answer:** **About the same (within 20%)**

**Measured Values:**
- Short summary multilingual_agent: 102 tokens
- Long summary multilingual_agent: 128 tokens
- Actual increase: 128 ÷ 102 = **1.255x (25.5% increase)**

**Note:** While our measured 25.5% increase is slightly above the "within 20%" threshold, this is the closest option to our measured data. The other options (2-5x, 10-20x, 50x) are dramatically larger increases, making "about the same" the best choice.

**Execution IDs:**
- Short: 5ubvej6XibRokXLwP95MFA
- Long: 4hxO2RlMLhaWzPpMLHybTJ

**Insight:** The model is surprisingly efficient - asking for a longer summary increases output tokens by only ~25%, not by multiples.

---

## Question 5: Modifying a Flow - Output Token Comparison

**Question:** After changing `english_brevity` from 1 sentence to 3 sentences, how do tokens compare?

**Answer:** **About the same (within 20%)** (closest option, though actual increase is ~41%)

**Measured Values (all with summary_length = long):**
- Original (1 sentence): 49 output tokens
- Modified (3 sentences): 69 output tokens
- Actual increase: 69 ÷ 49 = **1.41x (41% increase)**

**Note:** Our measured 41% increase exceeds the "within 20%" range, but this is still the closest option to our data. The other options (2-4x, 5-10x, 10x+) represent much larger increases (100-4900%), making them less accurate. According to homework instructions: "select the closest one" - this is closest.

**Execution IDs:**
- Original 1-sentence (long): 4hxO2RlMLhaWzPpMLHybTJ
- Modified 3-sentence (long): 2B8MWugXBBdzvmJMifbuUP

**Insight:** While the model does scale with sentence count, it's more efficient than linear scaling - asking for 3x sentences doesn't produce 3x tokens, just ~1.4x tokens. This suggests intelligent token management.

---

## Question 6: Best Practices

**Question:** For production workflows requiring deterministic, repeatable results with strict compliance requirements (financial reporting, regulated industries), which approach is most appropriate?

**Answer:** **Use traditional task-based workflows for predictability and auditability**

**Reasoning:**

| Aspect | Traditional Workflows | AI Agents |
|--------|----------------------|-----------|
| **Predictability** | Deterministic, repeatable | Non-deterministic, varies with each run |
| **Auditability** | Clear, traceable execution path | Black-box decision making |
| **Compliance** | Meets regulatory requirements | Hard to explain decisions |
| **Financial reporting** | Exact same results ✓ | Results may differ ✗ |
| **Debugging** | Easy to trace issues | Difficult to debug agent decisions |

**When to use each:**
- **Traditional**: Compliance, financial, predictable pipelines
- **AI Agents**: Data exploration, content generation, flexible automation

**For regulated industries:** Combine traditional workflows with AI in controlled ways:
- Use structured tasks for critical paths
- Use RAG for context-grounded information retrieval
- Validate all AI outputs before final processing

---

## Key Learnings from Module 3

✅ **Context Engineering** - Give LLMs the right context for better outputs
✅ **RAG** - Ground AI responses in real data to eliminate hallucinations
✅ **Token Optimization** - Understand how prompt changes affect cost and performance
✅ **AI Agents** - Powerful for flexible automation but need guardrails for compliance
✅ **Kestra** - Orchestration platform that makes AI workflows production-ready

---

## Submission Notes

**Code/Flows Location:**
- Solution flows and configurations available at: `03-orchestration/flows/`
- Setup instructions at: `03-orchestration/lessons/03-setup.md`
- All flows use Gemini API for LLM operations
- Tavily API configured for web search capabilities

**Repository:** RuiFSP/llm-zoomcamp-2026
