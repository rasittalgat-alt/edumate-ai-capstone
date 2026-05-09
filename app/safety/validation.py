"""
Input validation — mirrors the Safety_Check node in the n8n Orchestrator.
Returns an error string if invalid, None if safe.
"""
from app.config import VALID_MODES, INJECTION_PATTERNS


def validate_request(payload: dict) -> str | None:
    question = (payload.get("question") or "").strip()
    mode = (payload.get("mode") or "").lower().strip()

    if not question and mode != "evaluate":
        return "empty_question: Question cannot be empty."

    if mode not in VALID_MODES:
        return f"invalid_mode: '{mode}' is not supported. Use: {VALID_MODES}"

    q_lower = question.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in q_lower:
            return f"injection_attempt: Request blocked by safety filter."

    return None
