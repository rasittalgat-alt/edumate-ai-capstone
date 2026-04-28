# EduMate AI Capstone

## Multi-Agent Learning Companion Powered by n8n

EduMate AI is a capstone GenAI project that demonstrates an end-to-end multi-agent learning assistant. The system helps students understand educational materials, generate practice quizzes, evaluate answers, and track learning progress.

The project combines:

- Multi-agent orchestration with **n8n**
- Retrieval-Augmented Generation over educational materials
- External tool integration through MCP-compatible services
- Progress tracking in Google Sheets
- LLM behavior tests for positive, negative, and adversarial scenarios
- Observability, safety, and documentation for a complete capstone submission

---

## 1. Project Goal

The goal of EduMate AI is to create a practical AI learning companion that supports students during independent study.

The assistant can:

1. Retrieve relevant learning content from a domain-specific knowledge base.
2. Explain concepts in simple language.
3. Generate personalized quiz questions.
4. Evaluate student answers and provide feedback.
5. Save progress data for review and follow-up learning.

---

## 2. Problem Statement

Students often struggle to understand learning materials when information is spread across textbooks, notes, PDFs, and digital files. They also lack immediate feedback when studying alone.

Teachers and mentors may need a lightweight assistant that can help explain topics, generate practice questions, and track student progress without manually preparing every interaction.

EduMate AI addresses this problem with a multi-agent GenAI workflow that combines educational retrieval, explanation, assessment, and progress tracking.

---

## 3. Core Use Case

A student asks a question about a learning topic.

Example:

```text
Explain what an algorithm is in simple words.
```

The system then:

1. Validates the request.
2. Retrieves relevant educational content using RAG.
3. Generates a grounded explanation.
4. Creates a short quiz.
5. Evaluates the student's answer.
6. Saves progress to Google Sheets.
7. Returns a final response with feedback and sources.

---

## 4. Architecture Summary

```text
Student / User Interface
        |
        v
n8n Webhook / Chat Trigger
        |
        v
Input Validation & Safety Layer
        |
        v
n8n Orchestrator Workflow
        |
        +--> Content Agent --> RAG Service --> Vector Database
        |
        +--> Tutor Agent
        |
        +--> Quiz Agent
        |
        +--> Progress Agent --> MCP / Google Sheets
        |
        v
Final Response
```

---

## 5. Agent Roles

### Content Agent

Retrieves relevant educational context from the RAG knowledge base.

### Tutor Agent

Generates a clear, student-friendly explanation based on retrieved content.

### Quiz Agent

Generates practice questions and evaluates student answers.

### Progress Agent

Stores learning outcomes, quiz score, weak areas, and recommendations.

### Safety Layer

Validates input, detects harmful or adversarial prompts, and prevents unsafe or unsupported responses.

---

## 6. Technology Stack

| Layer | Technology |
|---|---|
| Orchestration | n8n |
| RAG API | Python + FastAPI |
| Vector Database | ChromaDB |
| LLM | OpenAI / Gemini / Ollama-compatible model |
| Embeddings | OpenAI embeddings / local embedding model |
| External Integration | MCP-compatible Google Sheets integration |
| Testing | Pytest |
| Observability | n8n execution logs, structured logs, optional Langfuse |
| Version Control | GitHub |

---

## 7. Repository Structure

```text
edumate-ai-capstone/
├── README.md
├── .env.example
├── docs/
│   ├── architecture_blueprint.md
│   ├── executive_summary.md
│   ├── self_review.md
│   └── demo_script.md
├── workflows/
│   └── edumate_ai_orchestrator.json
├── app/
│   ├── main.py
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── retriever.py
│   │   └── vector_store.py
│   ├── safety/
│   │   ├── validation.py
│   │   └── guardrails.py
│   ├── monitoring/
│   │   └── logger.py
│   └── config.py
├── data/
│   ├── raw/
│   └── processed/
├── tests/
│   ├── test_positive_flow.py
│   ├── test_negative_cases.py
│   ├── test_adversarial_prompts.py
│   └── test_rag_quality.py
└── requirements.txt
```

---

## 8. Setup Instructions

### 8.1 Clone the Repository

```bash
git clone https://github.com/rasittalgat-alt/edumate-ai-capstone.git
cd edumate-ai-capstone
```

### 8.2 Create Virtual Environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 8.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 8.4 Configure Environment Variables

Create a `.env` file based on `.env.example`.

```env
RAG_SERVICE_URL=http://localhost:8000
LLM_PROVIDER=
OPENAI_API_KEY=
GOOGLE_SHEETS_ID=
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=
```

Do not commit real credentials to GitHub.

### 8.5 Run RAG Service

```bash
uvicorn app.main:app --reload
```

### 8.6 Import n8n Workflow

Import the workflow file from:

```text
workflows/edumate_ai_orchestrator.json
```

Then configure credentials and environment variables in n8n.

---

## 9. Example API Request

```json
{
  "student_id": "student_001",
  "student_level": "beginner",
  "subject": "Computer Science",
  "topic": "Algorithms",
  "mode": "explain",
  "question": "What is an algorithm?",
  "student_answer": null
}
```

---

## 10. Example System Response

```json
{
  "trace_id": "edumate-2026-001",
  "status": "success",
  "mode": "explain",
  "answer": {
    "explanation": "An algorithm is a clear set of steps used to solve a problem.",
    "example": "A recipe is a simple example of an algorithm.",
    "sources": [
      {
        "source": "grade7_computer_science_notes.md",
        "section": "Algorithms"
      }
    ]
  },
  "quiz": [
    {
      "question_id": "q1",
      "question": "What is an algorithm in your own words?"
    }
  ],
  "progress": {
    "saved": true,
    "recommendation": "Practice identifying algorithms in daily life."
  }
}
```

---

## 11. Testing

The project includes automated and manual tests for LLM behavior validation.

### Test Categories

- Positive user flow
- RAG retrieval quality
- Negative edge cases
- Adversarial prompt handling
- Progress tracking failure handling

### Run Tests

```bash
pytest tests/
```

---

## 12. Demo Plan

The 2-5 minute demo should show:

1. Project problem and goal.
2. n8n workflow architecture.
3. Live learning question.
4. RAG-based explanation with sources.
5. Quiz generation and answer evaluation.
6. Progress saved to Google Sheets.
7. Positive and negative test execution.
8. Short code self-review.

---

## 13. Key Design Decisions

### Why n8n?

n8n provides visual workflow orchestration, API integrations, execution logs, and clear demonstration of agent collaboration.

### Why RAG?

RAG grounds the assistant's answers in educational materials and reduces hallucination risk.

### Why Google Sheets?

Google Sheets is simple, transparent, and easy to demonstrate as a progress tracker.

### Why separate RAG service?

A separate FastAPI RAG service keeps retrieval logic modular and makes the system easier to test and maintain.

---

## 14. Known Limitations

- MVP may cover only a limited number of subjects.
- Quiz evaluation is not a replacement for human grading.
- RAG quality depends on document preparation.
- External API and MCP failures may affect progress tracking.
- The system requires careful prompt design to reduce hallucinations.

---

## 15. Future Improvements

- Teacher dashboard
- Multi-language support
- Adaptive difficulty
- Long-term learning memory
- LMS integration
- Better RAG evaluation dataset
- Voice interface
- Student document upload support

---

## 16. Deliverables Checklist

- [ ] Architecture Blueprint
- [ ] Executive Summary
- [ ] README
- [ ] Code Repository
- [ ] n8n Workflow Export
- [ ] RAG Service
- [ ] Test Suite
- [ ] Self-Review
- [ ] Demo Script
- [ ] Video Demo Link
- [ ] Submission `.txt` file

---

## 17. Submission File Format

The final submission file should be named:

```text
Capstone_project_[your_name]_[your_last_name].txt
```

The file should contain:

```text
[your]@epam.com
https://github.com/rasittalgat-alt/edumate-ai-capstone
[video demo link]
```
