"""
Logging utility — structured logs for EduMate requests and agent calls.
"""
import logging
import sys


def get_logger(name: str = "edumate") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S"
        ))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def log_request(logger: logging.Logger, trace_id: str, mode: str, question: str):
    logger.info("trace=%s mode=%s question=%s", trace_id, mode, question[:80])


def log_response(logger: logging.Logger, trace_id: str, status: str, score: int = None):
    if score is not None:
        logger.info("trace=%s status=%s score=%d", trace_id, status, score)
    else:
        logger.info("trace=%s status=%s", trace_id, status)
