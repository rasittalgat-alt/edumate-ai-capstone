# EduMate — AI Learning Companion

EduMate is a multi-agent AI system that helps students learn through interactive explanations, quizzes, and instant answer evaluation. Built on n8n, Gemini, and Pinecone.

---

## Architecture

```
User / Browser (index.html)
        │
        ▼  POST /webhook/edumate-ai
EduMate_AI_Orchestrator
  ├─ Parse_Input       — extract question, mode, topic, running_score
  ├─ Safety_Check      — reject empty, invalid mode, or injections
  ├─ IF_Safe
  │    ├─ [safe]  ──▶ Execute_Content_Agent
  │    │                    ▼
  │    │           Gemini Embedding-001
  │    │                    ▼
  │    │           Pinecone (namespace: edumate_kb)
  │    │                    ▼
  │    │           Format_RAG_Context
  │    │                    ▼
  │    │          Execute_Tutor_Agent
  │    │                    ▼
  │    │           Build_Prompt → Gemini Flash LLM
  │    │                    ▼
  │    │           Parse_Output (structured JSON)
  │    │                    ▼
  │    │          Execute_Progress_Agent
  │    │                    ▼
  │    │           Google Sheets (EduMate_Progress)
  │    │                    ▼
  │    │          Build_Final_Response → HTTP 200
  │    │
  │    └─ [unsafe] ──▶ Build_Rejection → HTTP 400
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vanilla HTML/CSS/JS (`index.html`) |
| Orchestration | n8n (self-hosted) |
| LLM | Google Gemini Flash (`gemini-2.0-flash`) |
| Embedding | Google Gemini Embedding-001 (768-dim) |
| Vector Database | Pinecone (namespace: `edumate_kb`) |
| Knowledge Base | `EduMate_RAG_Knowledge_Base.docx` → chunked (200w / 50w overlap) |
| Progress Tracking | Google Sheets |
| Ingestion Script | Python (`run_ingestion.py`) |

---

## Supported Modes

| Mode | Description | Required fields |
|---|---|---|
| `explain` | RAG-grounded topic explanation + 3 quiz questions | `question`, `mode` |
| `quiz` | Generate 3 quiz questions on a topic | `question`, `mode`, `topic` |
| `evaluate` | Score a student's answer (0–100) with feedback | `question`, `mode`, `student_answer`, `topic`, `running_score` |

### Topics (9)
Machine Learning · Neural Networks · Python · Algorithms & Data Structures · Databases · Large Language Models · Prompt Engineering · AI Agents · Data Science

---

## How to Run the Frontend

Just open `index.html` in a browser — no build step needed.

The frontend points to the live n8n webhook. To run against your own n8n instance, update the `API_URL` constant at the top of the `<script>` section in `index.html`.

---

## Ingestion (Populate Knowledge Base)

Prerequisites: Python 3.9+, `python-docx` package

```bash
pip install python-docx
python run_ingestion.py
```

This reads `EduMate_RAG_Knowledge_Base.docx`, chunks each topic into 200-word segments with 50-word overlap, embeds them via Gemini, and upserts to Pinecone (~36 vectors total).

**Set your credentials in `run_ingestion.py`:**
```python
GEMINI_KEY    = 'YOUR_GEMINI_API_KEY'
PINECONE_KEY  = 'YOUR_PINECONE_API_KEY'
PINECONE_HOST = 'YOUR_PINECONE_HOST_URL'
```

---

## Importing Workflows into n8n

1. In n8n: **Workflows → Import from File**
2. Import in this order:
   - `workflows/Content_Agent.json`
   - `workflows/Tutor_Agent.json`
   - `workflows/Progress_Agent.json`
   - `workflows/edumate_ai_orchestrator.json`
3. In the Orchestrator, update the `workflowId` in each **Execute Workflow** node with the IDs assigned after import.
4. Configure credentials:
   - **Google Gemini**: Settings → Credentials → Add → Google Gemini (PaLM) → paste API key
   - **Google Sheets OAuth2**: Settings → Credentials → Add → Google Sheets OAuth2 → authorize
5. Activate all 4 workflows.

---

## Required Credentials

| Secret | Where used |
|---|---|
| `GEMINI_API_KEY` | Content Agent (embedding), Tutor Agent (LLM), Ingestion |
| `PINECONE_API_KEY` | Content Agent (vector query), Ingestion |
| `PINECONE_HOST` | Content Agent, Ingestion |
| Google Sheets OAuth2 | Progress Agent |
| `SPREADSHEET_ID` | Progress Agent — Append_To_Sheets node |

---

## Test the API

```bash
# Explain mode
curl -X POST https://n8n.sheshimai.cloud/webhook/edumate-ai \
  -H "Content-Type: application/json" \
  -d @tests/positive_explain.json

# Evaluate mode
curl -X POST https://n8n.sheshimai.cloud/webhook/edumate-ai \
  -H "Content-Type: application/json" \
  -d @tests/positive_evaluate.json

# Safety test (should return HTTP 400)
curl -X POST https://n8n.sheshimai.cloud/webhook/edumate-ai \
  -H "Content-Type: application/json" \
  -d @tests/adversarial_prompt_injection.json
```

See `tests/` for all 6 test scenarios.

---

## Project Structure

```
edumate-ai-capstone/
├── index.html                        # Frontend UI (EN / RU / KK)
├── run_ingestion.py                  # KB ingestion script
├── EduMate_RAG_Knowledge_Base.docx   # Source knowledge base (9 topics)
├── architecture_blueprint.md         # Detailed architecture documentation
├── workflows/
│   ├── edumate_ai_orchestrator.json  # Orchestrator workflow
│   ├── Content_Agent.json            # RAG retrieval agent
│   ├── Tutor_Agent.json              # LLM response agent
│   └── Progress_Agent.json           # Google Sheets logging agent
└── tests/
    ├── positive_explain.json
    ├── positive_quiz.json
    ├── positive_evaluate.json
    ├── negative_empty_question.json
    ├── negative_unknown_topic.json
    └── adversarial_prompt_injection.json
```

---

## Capstone Requirements Coverage

| Requirement | Status |
|---|---|
| Working Application | ✅ Live at sheshimai.cloud |
| Multi-agent architecture | ✅ Orchestrator + Content + Tutor + Progress |
| At least 3 agents | ✅ Content, Tutor, Progress |
| RAG pipeline | ✅ DOCX → Gemini Embedding → Pinecone → LLM |
| External tool integration | ✅ Google Sheets via Progress Agent |
| Inter-agent communication | ✅ n8n Execute Workflow |
| Testability | ✅ explain / quiz / evaluate + safety cases |
| Observability | ✅ n8n execution logs + Google Sheets |
| Real-world use case | ✅ AI learning companion |
