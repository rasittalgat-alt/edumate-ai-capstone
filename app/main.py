"""
EduMate Python client — sends requests to the n8n webhook and prints results.
Usage:
    python app/main.py explain "What is machine learning?"
    python app/main.py quiz "Neural Networks"
    python app/main.py evaluate "What is overfitting?" "Overfitting is when a model memorizes training data" --topic "Machine Learning" --score 85
"""
import sys
import json
import urllib.request
import urllib.error

from app.config import WEBHOOK_URL, VALID_MODES
from app.safety.validation import validate_request
from app.monitoring.logger import get_logger

logger = get_logger("edumate.client")


def call_edumate(payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(WEBHOOK_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        logger.error("HTTP %d: %s", e.code, body)
        return body
    except Exception as e:
        logger.error("Request failed: %s", e)
        return {"error": str(e)}


def main():
    args = sys.argv[1:]
    if not args or args[0] not in VALID_MODES:
        print(f"Usage: python app/main.py <mode> <question> [answer] [--topic T] [--score N]")
        print(f"Modes: {VALID_MODES}")
        sys.exit(1)

    mode = args[0]
    question = args[1] if len(args) > 1 else ""
    student_answer = ""
    topic = ""
    running_score = 0

    for i, a in enumerate(args):
        if a == "--topic" and i + 1 < len(args):
            topic = args[i + 1]
        if a == "--score" and i + 1 < len(args):
            running_score = int(args[i + 1])
    if mode == "evaluate" and len(args) > 2:
        student_answer = args[2]

    payload = {
        "question": question,
        "mode": mode,
        "student_answer": student_answer,
        "topic": topic,
        "running_score": running_score,
    }

    error = validate_request(payload)
    if error:
        print(f"Validation error: {error}")
        sys.exit(1)

    logger.info("Sending %s request: %s", mode, question[:60])
    result = call_edumate(payload)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
