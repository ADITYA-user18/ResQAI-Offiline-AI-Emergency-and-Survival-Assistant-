"""
config.py — ResQAI Backend Configuration & Constants
=====================================================
Central configuration system for the entire backend.
All paths, model settings, and tunable parameters live here.

Scope: Web/laptop system only.
       Backend runs on the user's PC/laptop and serves a web browser.
"""

import os
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# BASE PATHS
# ─────────────────────────────────────────────────────────────────────────────

# Root of the ResQAI project (two levels up from backend/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Backend directory
BACKEND_DIR = Path(__file__).resolve().parent

# Knowledge base directories
KNOWLEDGE_DIR        = PROJECT_ROOT / "knowledge"
EMBEDDINGS_DIR       = KNOWLEDGE_DIR / "embeddings"
PROCESSED_DIR        = KNOWLEDGE_DIR / "processed"

# FAISS index and metadata (pre-built — DO NOT REBUILD)
FAISS_INDEX_PATH     = EMBEDDINGS_DIR / "faiss.index"
METADATA_JSON_PATH   = EMBEDDINGS_DIR / "metadata.json"

# Processed knowledge JSON files
FIRSTAID_JSON_PATH   = PROCESSED_DIR / "firstaid.json"
SURVIVAL_JSON_PATH   = PROCESSED_DIR / "survival.json"
LEGAL_JSON_PATH      = PROCESSED_DIR / "legal.json"

# SQLite database (users + chat history — NOT embeddings)
DATABASE_DIR         = BACKEND_DIR / "database"
SQLITE_DB_PATH       = DATABASE_DIR / "resqai_chats.db"

# Logs directory
LOGS_DIR             = BACKEND_DIR / "logs"

# ─────────────────────────────────────────────────────────────────────────────
# OLLAMA CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

OLLAMA_BASE_URL      = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_GENERATE_URL  = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL      = f"{OLLAMA_BASE_URL}/api/tags"

# Single lightweight model for fast offline RAG response
OLLAMA_MODEL         = "phi3"

# Embedding model — must match the model used when FAISS index was built
EMBEDDING_MODEL      = "nomic-embed-text"

# Ollama request settings
OLLAMA_TIMEOUT_SEC   = 300           # seconds before giving up on LLM response
OLLAMA_STREAM        = True          # set True to enable streaming

# ─────────────────────────────────────────────────────────────────────────────
# RETRIEVAL / RAG SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

# Number of top FAISS results to retrieve per query
TOP_K_RESULTS        = 3

# Maximum characters of context text sent to the LLM
MAX_CONTEXT_CHARS    = 3000

# Minimum similarity score to include a chunk (0–1, lower = more lenient)
MIN_SIMILARITY_SCORE = 0.0           # FAISS L2 distance; 0 = no filtering

# ─────────────────────────────────────────────────────────────────────────────
# CHAT / SESSION SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

# How many previous messages to include as conversation context
CHAT_HISTORY_WINDOW  = 6            # last N messages (user + assistant pairs)

# Auto-generated chat title: max words taken from the first query
CHAT_TITLE_MAX_WORDS = 8

# ─────────────────────────────────────────────────────────────────────────────
# API / SERVER SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

API_HOST             = os.getenv("API_HOST", "0.0.0.0")
API_PORT             = int(os.getenv("API_PORT", 8000))
API_RELOAD           = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS origins for web browser access
CORS_ORIGINS = [
    "http://localhost:3000",    # React/Next.js web frontend dev server
    "http://localhost:5173",    # Vite web frontend dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*",                        # Allow all during development
]

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────

LOG_LEVEL            = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE             = LOGS_DIR / "resqai_backend.log"
LOG_MAX_BYTES        = 5 * 1024 * 1024   # 5 MB before rotation
LOG_BACKUP_COUNT     = 3

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION SETTINGS  (fully offline — no cloud services)
# ─────────────────────────────────────────────────────────────────────────────

# JWT secret key — CHANGE THIS in production via environment variable!
JWT_SECRET_KEY       = os.getenv("JWT_SECRET_KEY", "resqai-offline-secret-change-in-prod-2026")

# JWT signing algorithm
JWT_ALGORITHM        = "HS256"

# Token expiry: 30 days
JWT_EXPIRE_DAYS      = int(os.getenv("JWT_EXPIRE_DAYS", 30))

# bcrypt hashing cost factor (12 = strong, ~250ms on modern hardware)
BCRYPT_ROUNDS        = 12

# Username constraints
USERNAME_MIN_LEN     = 3
USERNAME_MAX_LEN     = 30
PASSWORD_MIN_LEN     = 6

# ─────────────────────────────────────────────────────────────────────────────
# EMERGENCY SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are ResQAI, an emergency AI assistant.
Answer the user's question clearly, safely, and concisely using ONLY the provided <context>. 
CRITICAL RULES:
1. You MUST always use short bullet points or numbered lists.
2. NEVER write long paragraphs. Keep instructions bite-sized.
3. NEVER mention "context", "available information", or output the <context> block itself. Just give the direct answer to the user's question.
"""
