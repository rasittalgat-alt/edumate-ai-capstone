# Executive Summary

# EduMate AI: Multi-Agent Learning Companion Powered by n8n

## 1. Overview

EduMate AI is a multi-agent Generative AI learning companion designed to help students understand educational materials, practice with personalized quizzes, and track learning progress.

The project was created as a Capstone solution to demonstrate an end-to-end GenAI system with multi-agent orchestration, Retrieval-Augmented Generation, MCP-enabled external tool integration, testing, observability, and real-world applicability.

EduMate AI uses n8n as the orchestration layer. Specialized agents collaborate to retrieve educational content, explain concepts, generate quizzes, evaluate student answers, and save learning progress to an external tracker.

---

## 2. Problem Statement

Students often face difficulties when learning independently. Educational content may be distributed across textbooks, notes, PDFs, and other digital files. When students do not understand a concept, they may not have immediate access to a teacher or mentor. They also often lack quick personalized feedback when practicing.

Teachers and mentors face a related challenge: creating explanations, quizzes, and progress reports manually takes time.

EduMate AI addresses this problem by providing an AI-powered learning assistant that can support students in real time while keeping responses grounded in approved educational materials.

---

## 3. Project Objectives

The main objectives of the project are:

1. Build a working multi-agent GenAI learning assistant.
2. Use RAG to retrieve information from a domain-specific educational knowledge base.
3. Use n8n to orchestrate agent collaboration.
4. Integrate an external tool through MCP-compatible workflow integration.
5. Track learning progress in Google Sheets.
6. Validate the system using positive, negative, and adversarial test scenarios.
7. Document architecture decisions, limitations, and trade-offs.

---

## 4. Solution Summary

EduMate AI follows a structured learning workflow:

1. A student asks a question about a topic.
2. The system validates the input and checks safety conditions.
3. The Content Agent retrieves relevant educational material using RAG.
4. The Tutor Agent explains the topic in simple language.
5. The Quiz Agent generates practice questions or evaluates the student's answer.
6. The Progress Agent saves the result and recommendation to Google Sheets.
7. The system returns a final response with explanation, feedback, sources, and next steps.

This approach makes the assistant more reliable than a generic chatbot because answers are grounded in a controlled knowledge base and include source attribution.

---

## 5. Architecture Highlights

The system is designed around the following components:

| Component | Purpose |
|---|---|
| n8n Orchestrator | Coordinates the complete multi-agent workflow |
| Content Agent | Retrieves relevant educational material through RAG |
| Tutor Agent | Generates explanations from retrieved context |
| Quiz Agent | Creates quizzes and evaluates answers |
| Progress Agent | Saves student progress to Google Sheets |
| Safety Layer | Validates inputs and handles adversarial prompts |
| FastAPI RAG Service | Provides document ingestion and retrieval endpoints |
| ChromaDB | Stores vectorized educational content |
| MCP / Google Sheets Integration | Tracks learning outcomes externally |

The architecture separates orchestration from retrieval logic. n8n manages workflow execution and agent communication, while the RAG service handles document processing and vector search.

---

## 6. Key Technical Decisions

### n8n for Orchestration

n8n was selected because it provides a visual workflow environment, easy API integration, execution logs, and clear demonstration of multi-agent collaboration. This makes it suitable for both rapid prototyping and Capstone presentation.

### RAG for Grounded Answers

Retrieval-Augmented Generation was selected to reduce hallucination risk and ensure that explanations are based on educational materials rather than unsupported model knowledge.

### Google Sheets for Progress Tracking

Google Sheets was selected as a lightweight progress tracker because it is simple, transparent, and easy to demonstrate. It allows reviewers to see how student activity and quiz results are stored.

### Separate RAG Service

A separate FastAPI-based RAG service keeps the retrieval pipeline modular and testable. This design also makes it easier to improve the vector database, chunking strategy, or embedding model without changing the whole orchestration workflow.

---

## 7. Business and Educational Value

EduMate AI provides value for both learners and educators.

For students, it offers:
- immediate explanations;
- personalized practice questions;
- feedback on answers;
- recommendations for next steps;
- a guided learning experience.

For teachers and education teams, it offers:
- automated quiz generation;
- basic progress tracking;
- reduced manual support workload;
- a foundation for future teacher dashboards or LMS integrations.

The solution can be adapted for schools, universities, corporate training, and self-learning platforms.

---

## 8. Validation Strategy

The system is designed to be validated through several test categories:

### Positive Tests

- Student asks about a topic available in the knowledge base.
- System retrieves relevant context.
- Tutor Agent generates a grounded explanation.
- Quiz Agent creates relevant questions.
- Progress Agent saves the result.

### Negative Tests

- Empty user question.
- Unknown topic not found in the knowledge base.
- Malformed request.
- Incorrect student answer.
- MCP or Google Sheets failure.

### Adversarial Tests

- Prompt injection attempt.
- Request to ignore sources.
- Request to manipulate quiz score.
- Unsafe or unrelated request.

These tests demonstrate that the system handles both normal and unexpected behavior.

---

## 9. Observability and Safety

The system includes observability and safety considerations from the design stage.

Observability includes:
- n8n execution logs;
- workflow run status;
- agent input and output tracking;
- error logging;
- optional LLM tracing with Langfuse;
- response time and retrieval score tracking.

Safety includes:
- input validation;
- content filtering;
- prompt injection handling;
- privacy-conscious progress tracking;
- source-based responses;
- graceful degradation when external services fail.

---

## 10. Results Expected from MVP

The MVP is expected to demonstrate:

1. A working n8n-based multi-agent workflow.
2. RAG-based retrieval over a small educational knowledge base.
3. AI-generated explanation grounded in retrieved content.
4. Quiz generation and answer evaluation.
5. Progress saved to Google Sheets.
6. Positive and negative test cases.
7. Clear documentation and demo readiness.

The MVP intentionally prioritizes a focused, working system over unnecessary complexity.

---

## 11. Limitations and Trade-offs

The main limitations are:

- The initial knowledge base may cover only one or two subjects.
- Quiz evaluation may not fully replace teacher assessment.
- RAG quality depends on the quality of source documents and chunking.
- Google Sheets is suitable for MVP but not a full learning management database.
- External LLM or MCP service failures may affect parts of the workflow.

These trade-offs are acceptable for the Capstone scope because the main objective is to demonstrate a complete, working, and explainable GenAI system.

---

## 12. Future Improvements

Potential future improvements include:

- teacher dashboard;
- adaptive learning paths;
- multi-language support;
- long-term learner memory;
- deeper analytics;
- LMS integration;
- voice-based learning interface;
- support for student-uploaded documents;
- more advanced RAG evaluation.

---

## 13. Conclusion

EduMate AI demonstrates how multi-agent GenAI systems can be applied to a real educational problem. The system combines n8n orchestration, RAG, external progress tracking, safety controls, and testing into a practical learning assistant.

The project is intentionally scoped as a realistic MVP that can be implemented, demonstrated, tested, and documented within Capstone constraints. It provides clear educational value while satisfying the required technical components: multi-agent architecture, RAG pipeline, MCP integration, inter-agent collaboration, testability, observability, and a demonstrable user flow.
