"""
RAG ingestion module — reads EduMate_RAG_Knowledge_Base.docx,
chunks each topic, embeds via Gemini, upserts to Pinecone.
Can be imported or run directly: python -m app.rag.ingest
"""
from docx import Document

from app.rag.retriever import embed
from app.rag.vector_store import upsert, delete
from app.monitoring.logger import get_logger

logger = get_logger("edumate.ingest")

DOCX_PATH    = "data/raw/EduMate_RAG_Knowledge_Base.docx"
CHUNK_SIZE   = 200
CHUNK_OVERLAP = 50

TOPIC_MAP = {
    "1. Machine Learning Fundamentals":        ("doc-ml-001",  "Machine Learning"),
    "2. Neural Networks and Deep Learning":    ("doc-nn-002",  "Neural Networks"),
    "3. Python Programming":                   ("doc-py-003",  "Python"),
    "4. Algorithms and Data Structures":       ("doc-alg-004", "Algorithms & Data Structures"),
    "5. Databases: SQL and NoSQL":             ("doc-db-005",  "Databases"),
    "6. Large Language Models (LLMs)":         ("doc-llm-006", "Large Language Models"),
    "7. Prompt Engineering Techniques":        ("doc-pe-007",  "Prompt Engineering"),
    "8. AI Agents: Tools, RAG and Automation": ("doc-agi-008", "AI Agents"),
    "9. Data Science: Pandas, Charts and EDA": ("doc-ds-009",  "Data Science"),
}


def chunk_text(text: str) -> list[str]:
    words = text.split()
    stride = CHUNK_SIZE - CHUNK_OVERLAP
    chunks, start = [], 0
    while start < len(words):
        end = min(start + CHUNK_SIZE, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += stride
    return chunks


def parse_docx(path: str) -> list[dict]:
    doc = Document(path)
    sections, current, in_sources = [], None, False
    for p in doc.paragraphs:
        t = p.text.strip()
        if not t:
            continue
        if p.style.name == "Heading 1" and any(c.isdigit() for c in t[:3]):
            if current:
                sections.append(current)
            current = {"heading": t, "body": [], "sources": []}
            in_sources = False
        elif p.style.name == "Heading 2" and t.lower() == "sources":
            in_sources = True
        elif current:
            (current["sources"] if in_sources else current["body"]).append(t)
    if current:
        sections.append(current)
    return sections


def run_ingestion():
    logger.info("Reading %s", DOCX_PATH)
    sections = parse_docx(DOCX_PATH)
    logger.info("Parsed %d sections", len(sections))

    old_ids = [v[0] for v in TOPIC_MAP.values()]
    logger.info("Deleting %d old vectors", len(old_ids))
    try:
        delete(old_ids)
    except Exception as e:
        logger.warning("Delete warning (may not exist): %s", e)

    all_vectors = []
    for section in sections:
        heading = section["heading"]
        if heading not in TOPIC_MAP:
            continue
        doc_id, title = TOPIC_MAP[heading]
        body = " ".join(section["body"])
        chunks = chunk_text(body)
        logger.info("%s — %d words → %d chunks", title, len(body.split()), len(chunks))
        for i, chunk in enumerate(chunks):
            vector = embed(chunk)
            all_vectors.append({
                "id": f"{doc_id}-c{i}",
                "values": vector,
                "metadata": {
                    "topic": title.lower().replace(" ", "_"),
                    "title": title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "text": chunk,
                    "sources": section["sources"],
                },
            })

    logger.info("Upserting %d chunks in batches of 10", len(all_vectors))
    for i in range(0, len(all_vectors), 10):
        batch = all_vectors[i:i + 10]
        result = upsert(batch)
        logger.info("Batch %d: %s", i // 10 + 1, result)

    logger.info("Done — %d vectors in namespace 'edumate_kb'", len(all_vectors))


if __name__ == "__main__":
    run_ingestion()
