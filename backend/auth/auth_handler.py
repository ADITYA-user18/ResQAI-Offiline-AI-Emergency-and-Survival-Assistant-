"""
auth/auth_handler.py — FastAPI Dependency Injection for Auth
============================================================
Provides the `get_current_user` FastAPI dependency.

Usage in protected routes:
    from auth.auth_handler import get_current_user, CurrentUser

    @router.get("/chats")
    async def get_chats(current_user: CurrentUser):
        # current_user.user_id  → UUID
        # current_user.username → display name
        return chat_service.get_chats_for_user(current_user.user_id)

How it works:
    1. FastAPI extracts the Bearer token from the Authorization header.
    2. get_current_user() decodes and validates it locally (no network call).
    3. If invalid → raises HTTP 401 immediately (request is rejected).
    4. If valid → injects a CurrentUser object into the route function.
    5. The route then uses current_user.user_id to filter data per user.
"""

from dataclasses import dataclass
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from auth.jwt_handler import decode_access_token
    from utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

# ── FastAPI's built-in Bearer token extractor ─────────────────────────────────
# Reads the "Authorization: Bearer <token>" header automatically.
# auto_error=False lets us return a custom 401 instead of FastAPI's default.
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """
    Represents the authenticated user extracted from a valid JWT.

    Injected into protected routes via FastAPI dependency injection.
    All protected routes use this to identify the calling user.
    """
    user_id:  str
    username: str


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> CurrentUser:
    """
    FastAPI dependency that extracts and validates the JWT token.

    Flow:
        Authorization: Bearer eyJhbGci...
                              ↓
        bearer_scheme extracts the token string
                              ↓
        decode_access_token() verifies locally (HS256)
                              ↓
        Returns CurrentUser or raises HTTP 401

    Args:
        credentials: Automatically injected by FastAPI from the Authorization header.

    Returns:
        CurrentUser with user_id and username.

    Raises:
        HTTP 401 — if token is missing, expired, or invalid.
    """
    # No token provided at all
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Include 'Authorization: Bearer <token>' header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token   = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id  = payload.get("sub")
    username = payload.get("username")

    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is malformed.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"Authenticated request from user '{username}' ({user_id})")
    return CurrentUser(user_id=user_id, username=username)


# ── Type alias for cleaner route signatures ───────────────────────────────────
# Use:  async def my_route(current_user: CurrentUser = Depends(get_current_user)):
# Or shorter with the alias below:
#       async def my_route(current_user: AuthDep):
from typing import Annotated
AuthDep = Annotated[CurrentUser, Depends(get_current_user)]
