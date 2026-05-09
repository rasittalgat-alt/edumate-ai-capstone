"""
Pinecone vector store helper — wraps query and upsert HTTP calls.
Used by both run_ingestion.py and the retriever module.
"""
import json
import urllib.request

from app.config import PINECONE_API_KEY, PINECONE_HOST, PINECONE_NAMESPACE


def _post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Api-Key", PINECONE_API_KEY)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def query(vector: list[float], top_k: int = 3) -> list[dict]:
    """Query Pinecone and return top-k matches with metadata."""
    result = _post(f"{PINECONE_HOST}/query", {
        "vector": vector,
        "topK": top_k,
        "includeMetadata": True,
        "namespace": PINECONE_NAMESPACE,
    })
    return result.get("matches", [])


def upsert(vectors: list[dict]) -> dict:
    """Upsert a list of {id, values, metadata} dicts to Pinecone."""
    return _post(f"{PINECONE_HOST}/vectors/upsert", {
        "vectors": vectors,
        "namespace": PINECONE_NAMESPACE,
    })


def delete(ids: list[str]) -> None:
    """Delete vectors by ID list."""
    _post(f"{PINECONE_HOST}/vectors/delete", {
        "ids": ids,
        "namespace": PINECONE_NAMESPACE,
    })
