"""
EduMate configuration — all tunables in one place.
Set environment variables or edit defaults here for local development.
"""
import os

# n8n webhook endpoint
WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://n8n.sheshimai.cloud/webhook/edumate-ai"
)

# External API keys (set via environment variables — never hardcode)
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_HOST    = os.getenv("PINECONE_HOST", "")
PINECONE_NAMESPACE = "edumate_kb"
PINECONE_TOP_K   = 3
EMBEDDING_DIM    = 768

# Supported interaction modes
VALID_MODES = ["explain", "quiz", "evaluate"]

# Human-readable topic labels (must match Pinecone metadata 'title' field)
TOPICS = [
    "Machine Learning",
    "Neural Networks",
    "Python",
    "Algorithms & Data Structures",
    "Databases",
    "Large Language Models",
    "Prompt Engineering",
    "AI Agents",
    "Data Science",
]

# Safety: blocked prompt patterns (checked case-insensitively)
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "reveal system prompt",
    "do not use sources",
    "change my score",
    "bypass safety",
    "ignore all instructions",
    "disregard previous",
    "jailbreak",
]
