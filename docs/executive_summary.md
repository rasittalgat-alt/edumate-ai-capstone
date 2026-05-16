# Executive Summary — EduMate AI

## Project

**EduMate AI** is a multi-agent Generative AI learning companion built as a Capstone project. It helps students learn through interactive topic explanations, practice quizzes, and instant answer evaluation — all powered by RAG over a curated educational knowledge base.

**Live system:** `https://n8n.sheshimai.cloud/webhook/edumate-ai`

---

## Problem

Students studying AI/CS topics independently often lack:
- **Immediate feedback** on whether they understand a concept
- **Grounded answers** tied to actual educational material (not hallucinated)
- **Progress tracking** to see improvement over time

---

## Solution

EduMate is a 4-agent pipeline orchestrated by n8n:

1. **Orchestrator** validates and routes every request (safety, mode dispatch)
2. **Content Agent** retrieves relevant knowledge chunks from Pinecone via Gemini embeddings (RAG)
3. **Tutor Agent** uses Gemini Flash to generate explanations, quizzes, or evaluations grounded in RAG context
4. **Progress Agent** logs every interaction to Google Sheets with scores and topic tracking

The frontend (`index.html`) is a zero-dependency single-page app supporting English and Kazakh.

---

## Key Technical Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Orchestration | n8n | Visual pipelines, execution logs, no backend server needed |
| LLM | Gemini Flash 2.5 | Fast, enforces raw JSON output, cost-effective |
| Embedding | Gemini Embedding-001 | Same API provider, 768-dim, consistent quality |
| Vector DB | Pinecone | Managed, serverless, instant semantic search |
| Knowledge Base | DOCX → chunked (200w/50w overlap) | ~36 vectors for better RAG precision than 9 flat docs |
| MCP tool | Brave Search via supergateway | Real-time web search in Tutor Agent when KB is insufficient; explicit MCP protocol |
| Progress | Google Sheets | Human-readable, shareable, zero infrastructure |
| Frontend | Vanilla HTML/JS | No build step, works offline, bilingual UI (EN/KK) |

---

## Capstone Requirements

| Requirement | How EduMate meets it |
|---|---|
| Working Application | ✅ Live system, accessible via browser |
| Multi-agent architecture | ✅ Orchestrator + 3 specialized agents |
| At least 3 agents | ✅ Content, Tutor, Progress |
| RAG pipeline | ✅ DOCX → Gemini Embedding → Pinecone → LLM |
| MCP integration | ✅ Brave Search MCP tool in Tutor Agent (HTTP Streamable, supergateway on VPS) |
| External tool integration | ✅ Google Sheets (Progress Agent) + Brave Search MCP (Tutor Agent) |
| Inter-agent communication | ✅ n8n Execute Workflow (full JSON propagation) |
| Safety layer | ✅ Prompt injection detection, mode validation, empty-input rejection |
| Testability | ✅ 6 test payloads: positive, negative, adversarial |
| Observability | ✅ n8n execution logs + Google Sheets per-interaction log |
| Real-world use case | ✅ AI learning companion for CS/AI education |

---

## Results & Business Value

### Technical Results
- **9 topics** available (ML, Neural Networks, Python, Algorithms, Databases, LLMs, Prompt Engineering, AI Agents, Data Science)
- **3 interaction modes**: explain, quiz, evaluate
- **~36 Pinecone vectors** (chunked for higher retrieval precision)
- **Score tracking**: individual score (0–100) + cumulative session score
- **Safety**: 8 injection patterns blocked before any LLM call
- **Multilingual UI**: English, Kazakh
- **MCP web search**: real-time Brave Search fallback when knowledge base is insufficient

### Business Value
- **Accessibility**: any student with a browser can get personalized AI tutoring at zero cost — no subscription, no app install, no account required
- **Grounded answers**: RAG over a curated knowledge base eliminates hallucinations on in-scope topics; Brave Search MCP handles out-of-scope queries with live web data
- **Scalability**: the n8n pipeline handles concurrent users without infrastructure changes; Pinecone and Google Sheets scale automatically
- **Multilingual reach**: English and Kazakh UI serves diverse student populations without separate deployments
- **Auditability**: every interaction is logged to Google Sheets with topic, score, and timestamp — instructors can track student progress without any additional tooling
- **Cost**: the entire stack runs on free tiers (Pinecone, Google Sheets, Gemini API free quota, GitHub Pages) — operational cost is effectively zero for a student-scale deployment

---

## Lessons Learned & Next Steps

### Lessons Learned
- **Visual orchestration accelerates debugging**: n8n's per-node execution logs made multi-agent failures immediately traceable without additional instrumentation
- **Chunking matters more than model choice**: switching from whole-document to 200-word chunked RAG improved answer grounding more than any prompt tuning
- **MCP transport requires careful matching**: the main integration challenge was aligning n8n's HTTP Streamable expectation with the stdio-based Brave Search server — solved via supergateway

### Potential Next Steps
- Add streaming responses to eliminate the 3–5 sec wait
- Implement session memory so the Tutor Agent can conduct multi-turn learning dialogues
- Add user authentication for persistent cross-device progress tracking
- Expand the knowledge base to cover more CS topics

---

## Limitations & Trade-offs

| Limitation | Notes |
|---|---|
| No real-time streaming | n8n webhook waits for full response (~3–5 sec) |
| Score is LLM-judged | Gemini evaluates answers subjectively; not deterministic |
| Pinecone free tier | Index may reset; re-run ingestion if empty |
| No user auth | Frontend is open; progress stored in localStorage |

---

## Files

| File | Purpose |
|---|---|
| `index.html` | Frontend UI (EN / KK) |
| `run_ingestion.py` | Knowledge base ingestion entry point |
| `data/raw/EduMate_RAG_Knowledge_Base.docx` | Source educational content |
| `data/processed/chunks.json` | 36 chunked knowledge base vectors |
| `workflows/` | 4 n8n agent workflow JSONs |
| `app/` | Python utility layer (config, safety, RAG, logging) |
| `tests/` | 6 test payload JSONs |
| `docs/architecture_blueprint.md` | Full technical architecture |
| `docs/self_review.md` | Architectural decisions and trade-offs |
