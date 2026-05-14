# Self-Review — EduMate AI

## Overview

This document reflects on the key architectural decisions, trade-offs, and lessons learned during the design and implementation of EduMate AI. It is intended for the exam committee as part of the capstone deliverables.

---

## Architectural Decisions

### 1. n8n as the Orchestration Layer

**Decision:** Use n8n (self-hosted, Docker) instead of a Python-based framework (LangChain, CrewAI, AutoGen).

**Rationale:** n8n provides per-node execution logs with full input/output visibility. In a multi-agent system where agents call each other sequentially, this observability is critical — a failure in the Tutor Agent is immediately traceable without additional instrumentation. Visual pipelines also make the architecture self-documenting.

**Trade-off:** n8n workflows are less portable than Python code. The logic lives in a JSON export rather than version-controlled source files. Mitigated by committing all four workflow JSONs to the repository.

---

### 2. RAG with Chunked DOCX (200w / 50w overlap)

**Decision:** Chunk each topic into 200-word segments with 50-word overlap instead of storing one vector per topic.

**Rationale:** A single 800-word topic document produces one vector. A query about a specific concept within that topic may match poorly if the concept is buried in the second paragraph. Chunking produces 36 vectors from 9 topics (~4 per topic), allowing Pinecone to return the most relevant paragraph rather than the most relevant document. Retrieval precision improved noticeably during testing.

**Trade-off:** More vectors = more Pinecone storage and slightly higher query latency. At 36 vectors this is negligible; the free tier supports up to 100k vectors.

---

### 3. MCP Integration via supergateway (HTTP Streamable)

**Decision:** Connect Brave Search to the Tutor Agent using the MCP protocol, running `@modelcontextprotocol/server-brave-search` behind `supergateway` on the VPS.

**Rationale:** The knowledge base is static (written in 2024). Students asking about recent AI developments — new models, 2025/2026 trends — would get outdated answers. The Brave Search MCP tool lets the Tutor Agent decide when to perform a live web search. The agent calls it autonomously when RAG context is insufficient.

**Why supergateway:** n8n's MCP Client Tool node (v1.2) requires an HTTP endpoint (HTTP Streamable or SSE). The official Brave Search MCP server is stdio-based. supergateway wraps it as an HTTP server on port 3100, reachable from n8n's Docker container via the bridge gateway IP `172.17.0.1`.

**Trade-off:** The MCP server is a separate process managed by pm2 on the VPS. If the VPS restarts without pm2 startup, the tool becomes unavailable. The agent continues to function (using RAG only) but loses real-time search. Mitigation: `pm2 save` + pm2 startup hook.

---

### 4. Safety Layer in the Orchestrator

**Decision:** Implement prompt injection detection and input validation before any LLM call.

**Rationale:** Without a safety gate, adversarial inputs such as "ignore previous instructions" or "you are now DAN" would reach the LLM. The Orchestrator's `Safety_Check` node matches 8 injection patterns using regex and rejects the request with HTTP 400 before incurring any API cost or producing harmful output.

**Trade-off:** Pattern-based detection is not exhaustive — a sufficiently creative injection may pass. A production system would add a dedicated guardrail LLM call. For this capstone, 8 patterns cover the most common adversarial classes.

---

### 5. Google Sheets for Progress Tracking

**Decision:** Log every interaction (topic, mode, score, timestamp) to Google Sheets rather than a database.

**Rationale:** Google Sheets is human-readable, shareable without additional infrastructure, and zero-cost. For a capstone demo, it provides immediate visibility into the audit trail. The Progress Agent appends rows with `continueOnFail: true`, ensuring a Sheets failure never breaks the main response flow.

**Trade-off:** Not suitable for high concurrency — concurrent writes can cause race conditions. For production, a proper database (Postgres, Firestore) would be necessary.

---

## What I Would Do Differently

1. **Add streaming responses** — the current webhook waits for a full response (~3–5 seconds). A streaming endpoint would significantly improve perceived UX.
2. **Add a memory layer** — the Tutor Agent has no session memory. Conversations start fresh each time. LangChain memory nodes or a Redis store would enable multi-turn learning dialogues.
3. **Measure RAG retrieval quality** — I validated retrieval qualitatively but did not implement precision/recall metrics. A proper evaluation set with ground-truth answers would quantify RAG quality.
4. **User authentication** — the frontend is open and progress is stored in localStorage. A simple auth layer (OAuth, magic link) would enable persistent cross-device progress tracking.

---

## Lessons Learned

- **Visual orchestration accelerates debugging.** The ability to click any n8n execution and see exactly what each agent received and returned saved significant debugging time.
- **Chunking matters more than model choice.** Switching from whole-document to chunked RAG improved answer grounding more than tuning the LLM temperature.
- **MCP protocol is straightforward to integrate** once the transport layer is correctly configured. The main friction was matching n8n's expected HTTP Streamable endpoint to the stdio-based MCP server — solved by supergateway.
