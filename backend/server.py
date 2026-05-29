"""
server.py — ResQAI FastAPI Application Entry Point
===================================================
The main FastAPI application. Now includes:
  - Offline-first JWT authentication
  - Multi-user support
  - Auth audit middleware
  - Auth routes (/auth/signup, /auth/login, /auth/logout, /auth/me)
  - All protected RAG + chat routes

Run with:
    python server.py
  or:
    uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

import sys
from pathlib import Path

# ── Ensure the backend directory is on the Python path ───────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    API_HOST, API_PORT, API_RELOAD,
    CORS_ORIGINS, OLLAMA_MODEL,
    SQLITE_DB_PATH,
)
from utils.logger import get_logger
from database.chat_db import init_database
from services.faiss_service import faiss_service
from services.knowledge_service import knowledge_service
from services.ollama_service import ollama_service
from middleware.error_handler import register_error_handlers
from middleware.auth_middleware import AuthAuditMiddleware
from routes.auth_routes import router as auth_router
from routes.ask_routes import router as ask_router
from routes.chat_routes import router as chat_router
from models.response_models import HealthResponse, RootResponse

logger = get_logger("resqai.server")

# ─────────────────────────────────────────────────────────────────────────────
# APP CREATION
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="ResQAI — Offline AI Emergency Assistant",
    description=(
        "A RAG-powered offline emergency assistant with multi-user authentication. "
        "Provides first aid, survival, and legal guidance using FAISS + Ollama. "
        "All auth is local — no internet required.\n\n"
        "**Auth flow:** POST /auth/signup or /auth/login → receive JWT → "
        "include as `Authorization: Bearer <token>` on all other requests."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ─────────────────────────────────────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────────────────────────────────────

# 1. CORS — must be registered BEFORE other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Auth audit logging middleware
app.add_middleware(AuthAuditMiddleware)

# 3. Global error → clean JSON error handler
register_error_handlers(app)

# ─────────────────────────────────────────────────────────────────────────────
# STARTUP / SHUTDOWN EVENTS
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup() -> None:
    """
    Initialize all services when the FastAPI server starts.

    Order:
        1. SQLite (creates users + chats + messages tables)
        2. Knowledge service (loads processed JSONs into memory)
        3. FAISS service (loads vector index — read-only)
        4. Ollama health check
    """
    logger.info("=" * 60)
    logger.info("  ResQAI Backend v2.0 Starting Up")
    logger.info(f"  Model: {OLLAMA_MODEL}")
    logger.info("  Auth: Offline JWT + bcrypt (local SQLite)")
    logger.info("=" * 60)

    # 1. Initialize SQLite (creates users table + chats + messages)
    try:
        init_database()
        logger.info("[OK] SQLite database initialized (users + chats + messages)")
    except Exception as e:
        logger.critical(f"[ERROR] SQLite initialization failed: {e}")
        raise

    # 2. Load processed knowledge files
    try:
        knowledge_service.load()
        logger.info(f"[OK] Knowledge service loaded ({knowledge_service.chunk_count} chunks)")
    except Exception as e:
        logger.error(f"[ERROR] Knowledge service failed: {e} — continuing without it")

    # 3. Load FAISS index
    try:
        faiss_service.load()
        logger.info(
            f"[OK] FAISS service loaded "
            f"({faiss_service.vector_count} vectors, d={faiss_service.dimension})"
        )
    except FileNotFoundError as e:
        logger.error(f"[ERROR] FAISS index not found: {e}")
    except Exception as e:
        logger.error(f"[ERROR] FAISS service failed: {e}")

    # 4. Ollama availability check
    if ollama_service.is_available():
        logger.info(f"[OK] Ollama available — model: {OLLAMA_MODEL}")
    else:
        logger.warning(
            f"[WARN] Ollama unavailable or model '{OLLAMA_MODEL}' not pulled. "
            f"Run: `ollama pull {OLLAMA_MODEL}` then `ollama serve`"
        )

    logger.info("=" * 60)
    logger.info(f"  API docs: http://{API_HOST}:{API_PORT}/docs")
    logger.info("  ResQAI Backend is READY")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("ResQAI Backend shutting down. Goodbye.")


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

# Public auth routes  (no JWT needed to signup/login)
app.include_router(auth_router)

# Protected RAG + chat routes (JWT required on every request)
app.include_router(ask_router)
app.include_router(chat_router)


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/",
    response_model=RootResponse,
    tags=["System"],
    summary="API root",
)
async def root() -> RootResponse:
    return RootResponse(
        app="ResQAI — Offline AI Emergency Assistant v2.0",
        version="2.0.0",
        status="running",
        docs=f"http://{API_HOST}:{API_PORT}/docs",
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description=(
        "Returns component health: FAISS, knowledge base, Ollama, and SQLite. "
        "Does not require authentication."
    ),
)
async def health_check() -> HealthResponse:
    faiss_ok     = faiss_service.is_loaded
    knowledge_ok = knowledge_service.is_loaded
    ollama_ok    = ollama_service.is_available()

    if faiss_ok and knowledge_ok and ollama_ok:
        status = "healthy"
    elif faiss_ok and knowledge_ok:
        status = "degraded"
    else:
        status = "unhealthy"

    return HealthResponse(
        status=status,
        faiss_loaded=faiss_ok,
        knowledge_loaded=knowledge_ok,
        ollama_available=ollama_ok,
        model=OLLAMA_MODEL,
        vector_count=faiss_service.vector_count,
        chunk_count=knowledge_service.chunk_count,
        database=str(SQLITE_DB_PATH),
    )


# ─────────────────────────────────────────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=API_HOST,
        port=API_PORT,
        reload=API_RELOAD,
        log_level="info",
    )
