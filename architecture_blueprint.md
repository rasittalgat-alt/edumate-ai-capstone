# EduMate Architecture Blueprint

## Overview

EduMate is a multi-agent AI tutoring system. All orchestration runs on **n8n** (self-hosted at `n8n.sheshimai.cloud`). There is no separate backend server — n8n handles all routing, agent execution, and external API calls.

---

## System Components

### Frontend
- **File:** `index.html`
- **Tech:** Vanilla HTML/CSS/JavaScript (no framework, no build step)
- **State:** `localStorage` key `edumate_progress_v2` stores quiz history and scores locally in the browser
- **Languages:** English, Russian, Kazakh (switched via `LANG` variable)
- **Entrypoint:** User opens `index.html` → selects a topic → sends POST to n8n webhook

### Orchestrator — EduMate_AI_Orchestrator
- **Trigger:** `POST /webhook/edumate-ai`
- **Nodes:**
  1. `Webhook` — receives request
  2. `Parse_Input` — extracts `question`, `mode`, `topic`, `student_answer`, `running_score`, generates `trace_id`
  3. `Safety_Check` — rejects empty questions, invalid modes, prompt injection attempts
  4. `IF_Safe` — routes: safe → agent pipeline, unsafe → rejection response
  5. `Execute_Content_Agent` → `Execute_Tutor_Agent` → `Execute_Progress_Agent` (sequential)
  6. `Build_Final_Response` — assembles mode-specific response object
  7. `Respond_Success` / `Respond_Rejected` — returns HTTP 200 or 400

### Content Agent — EduMate_Content_Agent
- **Trigger:** Called by Orchestrator via `executeWorkflow`
- **Nodes:**
  1. `Prepare_Embed_Request` — passes `question` as embed text
  2. `Call_Gemini_Embedding` — `gemini-embedding-001`, 768 dimensions
  3. `Prepare_Pinecone_Query` — extracts embedding vector
  4. `Query_Pinecone` — `topK: 3`, namespace `edumate_kb`
  5. `Format_RAG_Context` — builds `rag_context` string + `sources` list; graceful fallback if no matches

### Tutor Agent — EduMate_Tutor_Agent
- **Trigger:** Called by Orchestrator via `executeWorkflow`
- **LLM:** Google Gemini Flash (via n8n LangChain agent node)
- **Nodes:**
  1. `Build_Prompt` — constructs mode-specific prompt with RAG context injected
  2. `AI Agent` (LangChain) — system prompt enforces raw JSON output
  3. `Google Gemini Chat Model` — `temperature: 0.7`
  4. `Parse_Output` — strips markdown fences, parses JSON; fallback on parse error

**Prompt formats by mode:**

| Mode | LLM output schema |
|---|---|
| `explain` | `{explanation, example, quiz: [{question, answer}×3], recommendation}` |
| `quiz` | `{quiz: [{question, answer}×3]}` |
| `evaluate` | `{correct, partial_credit, score, feedback, correct_answer}` |

### Progress Agent — EduMate_Progress_Agent
- **Trigger:** Called by Orchestrator via `executeWorkflow`
- **Nodes:**
  1. `Prepare_Progress` — computes `evaluation_result`, `score`, `overall_score = running_score + llm.score`
  2. `Append_To_Sheets` — appends row to Google Sheets (`continueOnFail: true`)
  3. `Return_Status` — returns `progress_saved` flag to orchestrator

**Google Sheets schema (9 columns):**

| Column | Description |
|---|---|
| `timestamp` | ISO 8601 UTC |
| `trace_id` | Unique request ID |
| `question` | Student's question or quiz question |
| `mode` | `explain` / `quiz` / `evaluate` |
| `student_answer` | Student's answer (evaluate mode only) |
| `evaluation_result` | `correct` / `partial` / `incorrect` |
| `score` | Individual question score (0–100) |
| `topic` | Human-readable topic name (e.g., "Data Science") |
| `overall_score` | Cumulative score across quiz session |

---

## Knowledge Base

- **Source:** `EduMate_RAG_Knowledge_Base.docx` (9 topics, Word document)
- **Processing:** `run_ingestion.py`
  1. Parse `.docx` by Heading 1 sections
  2. Chunk each topic body: 200 words, 50-word overlap
  3. Embed each chunk: `gemini-embedding-001` → 768-dim vector
  4. Upsert to Pinecone: namespace `edumate_kb`, ~36 vectors total

**Topics in knowledge base:**

| ID | Topic |
|---|---|
| `doc-ml-001` | Machine Learning Fundamentals |
| `doc-nn-002` | Neural Networks & Deep Learning |
| `doc-py-003` | Python Programming |
| `doc-alg-004` | Algorithms & Data Structures |
| `doc-db-005` | Databases: SQL & NoSQL |
| `doc-llm-006` | Large Language Models |
| `doc-pe-007` | Prompt Engineering Techniques |
| `doc-agi-008` | AI Agents: Tools, RAG & Automation |
| `doc-ds-009` | Data Science: Pandas, Charts & EDA |

---

## Data Flow — Sequence Diagrams

### Explain Mode

```
Browser          Orchestrator      ContentAgent      TutorAgent        ProgressAgent     Sheets
   │                  │                 │                 │                  │              │
   │──POST explain──▶ │                 │                 │                  │              │
   │                  │─Parse+Safety──▶ │                 │                  │              │
   │                  │─executeWF──────▶│                 │                  │              │
   │                  │                 │─Gemini embed──▶ │                  │              │
   │                  │                 │─Pinecone query─▶│                  │              │
   │                  │                 │◀─top-3 chunks───│                  │              │
   │                  │◀────rag_context─│                 │                  │              │
   │                  │─executeWF───────────────────────▶ │                  │              │
   │                  │                 │                 │─Gemini Flash LLM─▶              │
   │                  │                 │                 │◀─JSON response────▶              │
   │                  │◀────llm_output──────────────────── │                  │              │
   │                  │─executeWF────────────────────────────────────────────▶│              │
   │                  │                 │                 │                  │──append──────▶│
   │                  │◀───progress_saved──────────────────────────────────── │              │
   │◀─HTTP 200────────│                 │                 │                  │              │
```

### Evaluate Mode

```
Browser → Orchestrator: { question, mode:"evaluate", student_answer, topic, running_score }
Orchestrator → ContentAgent: embed student_answer, retrieve context
ContentAgent → TutorAgent: rag_context + student_answer
TutorAgent → Gemini: score answer 0-100, provide feedback
TutorAgent → ProgressAgent: llm_output { correct, score, feedback }
ProgressAgent: overall_score = running_score + llm.score → append to Sheets
Orchestrator → Browser: { evaluation: { score, feedback, correct_answer }, progress: { saved } }
```

---

## Safety Layer

The `Safety_Check` node in the Orchestrator blocks:
- Empty questions (when mode ≠ evaluate)
- Invalid mode values (only `explain`, `quiz`, `evaluate` allowed)
- Prompt injection patterns (8 keywords checked case-insensitively)

Blocked requests return HTTP 400 with `{ status: "rejected", error, message }`.

---

## Inter-Agent Communication

n8n's `executeWorkflow` node passes the current data item to the child workflow's `executeWorkflowTrigger`. Each agent receives the full accumulated JSON from upstream agents and extends it (spread pattern `{ ...data, newField }`). This ensures all fields (including `topic`, `running_score`) are available at every stage.

---

## Deployment

- **n8n instance:** `https://n8n.sheshimai.cloud` (Docker, self-hosted on VPS)
- **Webhook URL:** `https://n8n.sheshimai.cloud/webhook/edumate-ai`
- **All 4 workflows active**
- **Frontend:** `index.html` served statically (can be opened locally or hosted on any static host)
