"""
middleware/error_handler.py — Global Error Handling Middleware
==============================================================
Catches unhandled exceptions from any route and returns structured
JSON error responses (never raw Python tracebacks to the client).

Also registers per-type exception handlers for common errors.
"""

import traceback
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers on the FastAPI app instance.
    Call this in server.py after creating the app.

    Args:
        app: The FastAPI application instance.
    """

    # ── 422 Validation errors (Pydantic) ──────────────────────────────────────
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        logger.warning(
            f"Validation error on {request.method} {request.url.path}: {errors}"
        )
        return JSONResponse(
            status_code=422,
            content={
                "error":   "Validation Error",
                "detail":  errors,
                "message": "Request data is invalid. Check the required fields.",
            },
        )

    # ── HTTP errors (404, 405, etc.) ──────────────────────────────────────────
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        logger.warning(
            f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error":   "HTTP Error",
                "status":  exc.status_code,
                "message": exc.detail or "An HTTP error occurred.",
            },
        )

    # ── Ollama connection errors ───────────────────────────────────────────────
    @app.exception_handler(ConnectionError)
    async def connection_error_handler(
        request: Request, exc: ConnectionError
    ) -> JSONResponse:
        logger.error(f"Connection error: {exc}")
        return JSONResponse(
            status_code=503,
            content={
                "error":   "Service Unavailable",
                "message": str(exc),
                "hint":    "Make sure Ollama is running: `ollama serve`",
            },
        )

    # ── General catch-all ─────────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        tb = traceback.format_exc()
        logger.error(
            f"Unhandled exception on {request.method} {request.url.path}:\n{tb}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "error":   "Internal Server Error",
                "message": "An unexpected error occurred. Check server logs.",
                "type":    type(exc).__name__,
            },
        )
