"""
Guardrails — topic scope check and response sanitization.
"""
from app.config import TOPICS


def is_on_topic(question: str) -> bool:
    """Heuristic: check if question mentions any known topic keyword."""
    q = question.lower()
    keywords = [t.lower() for t in TOPICS] + [
        "ml", "ai", "neural", "algorithm", "database", "sql", "nosql",
        "llm", "gpt", "bert", "transformer", "embedding", "pandas",
        "numpy", "eda", "rag", "agent", "python", "classification",
        "regression", "clustering", "overfitting", "gradient",
    ]
    return any(kw in q for kw in keywords)


def sanitize_response(text: str) -> str:
    """Strip leading/trailing whitespace and null bytes from LLM output."""
    return text.strip().replace("\x00", "")
