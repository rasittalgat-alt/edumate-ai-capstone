# EduMate AI — Architecture Blueprint

## 1. Project Overview

**EduMate AI** is a multi-agent Generative AI learning companion that helps students understand educational topics, practice with personalized quizzes, and track their learning progress. All orchestration is handled by **n8n** — no separate backend server is needed.

**Live system:** `https://n8n.sheshimai.cloud/webhook/edumate-ai`

---

## 2. System Architecture

```
User / Browser (index.html)
        │
        ▼  POST /webhook/edumate-ai
        │  { question, mode, topic, student_answer, running_score }
        │
┌───────────────────────────────────┐
│     EduMate_AI_Orchestrator       │
│  ┌─────────────┐                  │
│  │ Parse_Input │ trace_id, mode,  │
│  │             │ topic, score     │
│  └──────┬──────┘                  │
│         ▼                         │
│  ┌──────────────┐                 │
│  │ Safety_Check │ empty / mode /  │
│  │              │ injection check │
│  └──────┬───────┘                 │
│         ▼                         │
│      IF_Safe                      │
│    ┌────┴────┐                    │
│  safe     unsafe                  │
│    │         └──▶ Reject (400)    │
│    ▼                              │
│  Execute_Content_Agent            │
│    ▼                              │
│  Execute_Tutor_Agent              │
│    ▼                              │
│  Execute_Progress_Agent           │
│    ▼                              │
│  Build_Final_Response → 200       │
└───────────────────────────────────┘
```

---

## 3. Agent Descriptions

### Content Agent — EduMate_Content_Agent
**Role:** Retrieves relevant educational context from Pinecone using RAG.

| Node | Action |
|---|---|
| Prepare_Embed_Request | Passes question as embed text |
| Call_Gemini_Embedding | `gemini-embedding-001` → 768-dim vector |
| Prepare_Pinecone_Query | Extracts embedding values |
| Query_Pinecone | `topK: 3`, namespace `edumate_kb` |
| Format_RAG_Context | Builds `rag_context` string + `sources[]`; fallback if no matches |

### Tutor Agent — EduMate_Tutor_Agent
**Role:** Generates a structured LLM response using RAG context, with Brave Search available via MCP for supplementary web lookups.

| Node | Action |
|---|---|
| Build_Prompt | Constructs mode-specific prompt with injected RAG context |
| AI Agent (LangChain) | System prompt enforces raw JSON output only |
| Google Gemini Chat Model | `gemini-2.5-flash`, temperature 0.7 |
| Brave_Search_MCP | MCP Client Tool v1.2 — HTTP Streamable transport to `http://172.17.0.1:3100/mcp` |
| Parse_Output | Strips markdown fences, parses JSON; fallback on error |

**Output schema by mode:**

| Mode | JSON structure |
|---|---|
| `explain` | `{explanation, example, quiz:[{question,answer}×3], recommendation}` |
| `quiz` | `{quiz:[{question,answer}×3]}` |
| `evaluate` | `{correct, partial_credit, score, feedback, correct_answer}` |

### Progress Agent — EduMate_Progress_Agent
**Role:** Logs every interaction to Google Sheets for observability and student tracking.

| Node | Action |
|---|---|
| Prepare_Progress | Computes `overall_score = running_score + llm.score` |
| Append_To_Sheets | Appends row (`continueOnFail: true` — never breaks main flow) |
| Return_Status | Returns `progress_saved` flag to orchestrator |

**Google Sheets schema (9 columns):**

| Column | Description |
|---|---|
| `timestamp` | ISO 8601 UTC |
| `trace_id` | Unique request ID |
| `question` | Student's question |
| `mode` | explain / quiz / evaluate |
| `student_answer` | Student answer (evaluate only) |
| `evaluation_result` | correct / partial / incorrect |
| `score` | Individual score 0–100 |
| `topic` | Human-readable topic (e.g. "Data Science") |
| `overall_score` | Cumulative score across quiz session |

---

## 4. Knowledge Base & RAG Pipeline

```
EduMate_RAG_Knowledge_Base.docx
        │
        ▼ parse_docx() — extract Heading 1 sections
        │
        ▼ chunk_text() — 200 words, 50-word overlap → ~36 chunks
        │
        ▼ gemini-embedding-001 → 768-dim vectors
        │
        ▼ Pinecone upsert (namespace: edumate_kb)
```

**9 topics indexed:**

| ID | Title |
|---|---|
| doc-ml-001 | Machine Learning |
| doc-nn-002 | Neural Networks |
| doc-py-003 | Python Programming |
| doc-alg-004 | Algorithms & Data Structures |
| doc-db-005 | Databases: SQL & NoSQL |
| doc-llm-006 | Large Language Models |
| doc-pe-007 | Prompt Engineering |
| doc-agi-008 | AI Agents |
| doc-ds-009 | Data Science |

---

## 5. Technology Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend | Vanilla HTML/CSS/JS | Zero dependencies, bilingual UI (EN/KK) |
| Orchestration | n8n (self-hosted Docker) | Visual agent pipeline, execution logs |
| LLM | Gemini Flash 2.5 | Fast, structured JSON output |
| Embedding | Gemini Embedding-001 (768-dim) | Same provider, consistent latency |
| Vector DB | Pinecone | Managed, serverless, instant RAG |
| Progress | Google Sheets | Human-readable, zero infrastructure |
| External Search | Brave Search via MCP protocol | Real-time web context when KB is insufficient; satisfies MCP requirement |
| MCP Transport | supergateway (HTTP Streamable) | Wraps stdio MCP server as HTTP endpoint for n8n |
| Ingestion | Python (`run_ingestion.py`, `app/rag/`) | One-time batch script |

---

## 6. MCP Integration

The Tutor Agent connects to an external Brave Search MCP server via n8n's **MCP Client Tool** node (v1.2, HTTP Streamable transport). This enables the AI agent to perform live web searches when the RAG knowledge base is insufficient.

```
Tutor Agent (AI Agent node)
        │
        ▼ ai_tool connection
Brave_Search_MCP node
  endpointUrl: http://172.17.0.1:3100/mcp
  transport:   httpStreamable
        │
        ▼ Docker bridge (172.17.0.1)
VPS Host Machine
  supergateway v3.4.3  (port 3100)
    --outputTransport streamableHttp /mcp
        │
        ▼ stdio
  @modelcontextprotocol/server-brave-search
    BRAVE_API_KEY=...
```

**Setup (on VPS / host):**
```bash
npm install -g supergateway @modelcontextprotocol/server-brave-search pm2
BRAVE_API_KEY=your_key pm2 start supergateway --name mcp-brave -- \
  --port 3100 --stdio "npx -y @modelcontextprotocol/server-brave-search" \
  --outputTransport streamableHttp --cors
pm2 save
```

---

## 7. Safety Layer

The `Safety_Check` node in the Orchestrator blocks requests before any LLM call:

| Check | Condition | Response |
|---|---|---|
| Empty question | `question == ""` and mode ≠ evaluate | 400 `empty_question` |
| Invalid mode | mode ∉ {explain, quiz, evaluate} | 400 `invalid_mode` |
| Prompt injection | matches any of 8 injection patterns | 400 `injection_attempt` |

All blocked requests return `{ status: "rejected", error, message }` with HTTP 400.

---

## 8. Inter-Agent Communication

n8n's `executeWorkflow` node passes the **full accumulated JSON** to each child workflow. Each agent receives all upstream fields and extends them with new fields (`spread pattern: { ...data, newField }`). This ensures `topic`, `running_score`, `rag_context`, and `llm_output` are available at every stage.

---

## 9. Frontend (index.html)

- **Modes:** Explain, Quiz, Evaluate
- **Languages:** English, Kazakh (switched in real time)
- **Progress tracking:** `localStorage` key `edumate_progress_v2`
- **API:** `fetch()` POST to n8n webhook, handles JSON response
- **Quiz state:** `qs.runningScore` accumulates across 3 questions → sent as `running_score` to backend

---

## 10. Observability

| Source | What it shows |
|---|---|
| n8n execution logs | Full node-by-node trace, input/output per agent |
| Google Sheets | Per-interaction log: mode, topic, score, overall progress |
| `trace_id` field | Correlates frontend request with n8n execution |

---

## 11. Deployment

- **n8n:** Docker, self-hosted at `n8n.sheshimai.cloud` (VPS, Let's Encrypt via Traefik)
- **Frontend:** Static HTML — served locally or on any static host
- **Knowledge Base:** Ingested once via `run_ingestion.py`; re-run if DOCX changes
