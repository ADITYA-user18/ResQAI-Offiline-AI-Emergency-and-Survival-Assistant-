"""
middleware/auth_middleware.py — Auth Logging Middleware
=======================================================
Request-level logging for security observability.
Logs every incoming request with its authentication status.

This middleware does NOT block requests — actual auth enforcement
is done by the `get_current_user` dependency on each protected route.
This middleware only provides audit logging.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

try:
    from utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("resqai.auth_audit")

# Paths that don't require auth (public endpoints)
PUBLIC_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json",
                "/auth/login", "/auth/signup"}


class AuthAuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all incoming requests with timing and auth status.

    Logged fields:
        - HTTP method and path
        - Whether a Bearer token was present
        - Response status code
        - Request duration (ms)

    Note: Does NOT validate the token — that's the dependency's job.
    This is purely for audit/observability.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        # Check if Authorization header is present
        auth_header = request.headers.get("Authorization", "")
        has_token   = auth_header.startswith("Bearer ")
        path        = request.url.path
        is_public   = path in PUBLIC_PATHS

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Audit log
        auth_status = (
            "public" if is_public
            else ("authenticated" if has_token else "UNAUTHENTICATED")
        )

        logger.info(
            f"{request.method} {path} | "
            f"status={response.status_code} | "
            f"auth={auth_status} | "
            f"{duration_ms:.1f}ms"
        )

        return response
