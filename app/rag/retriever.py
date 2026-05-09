"""
RAG retriever — embeds a question via Gemini and queries Pinecone.
Returns (rag_context: str, sources: list[str]).
"""
import json
import urllib.request

from app.config import GEMINI_API_KEY, EMBEDDING_DIM
from app.rag.vector_store import query

EMBED_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-embedding-001:embedContent?key={GEMINI_API_KEY}"
)


def embed(text: str) -> list[float]:
    payload = {
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": EMBEDDING_DIM,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(EMBED_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["embedding"]["values"]


def retrieve(question: str, top_k: int = 3) -> tuple[str, list[str]]:
    """
    Embed the question, query Pinecone, return formatted context + source list.
    Falls back to generic context if no matches found.
    """
    vector = embed(question)
    matches = query(vector, top_k=top_k)

    if not matches:
        context = (
            f"Educational material on {question}. "
            "Focus on foundational concepts and practical applications."
        )
        return context, ["Course Curriculum", "Academic Reference Library"]

    contexts, sources = [], []
    for i, m in enumerate(matches):
        meta = m.get("metadata", {})
        if meta.get("text"):
            contexts.append(f"Source {i+1}: {meta.get('title','Reference')}\n{meta['text']}")
            for s in (meta.get("sources") or []):
                if s not in sources:
                    sources.append(s)

    return "\n\n".join(contexts), sources
