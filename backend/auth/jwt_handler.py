"""
auth/jwt_handler.py — Offline JWT Token Management
===================================================
Creates and validates JWT tokens entirely locally using HS256.
No network call is ever made during token operations.

Token lifecycle:
  1. User logs in (credentials verified against SQLite)
  2. Server signs a JWT with the local secret key
  3. Client stores the token (localStorage / SecureStore)
  4. Client sends token in Authorization header on every request
  5. Server verifies the signature and expiry locally
  6. User identity is extracted from the verified payload

Why this works offline:
  - HS256 is symmetric: same secret key signs and verifies
  - The secret lives locally on the device/server
  - No remote auth service is ever contacted
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

try:
    import jwt as pyjwt  # pip install PyJWT
except ImportError:
    raise ImportError("PyJWT is not installed. Run: pip install PyJWT")

try:
    from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRE_DAYS
    from utils.logger import get_logger
except ImportError:
    JWT_SECRET_KEY  = "resqai-offline-secret"
    JWT_ALGORITHM   = "HS256"
    JWT_EXPIRE_DAYS = 30
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


def create_access_token(user_id: str, username: str) -> str:
    """
    Create a signed JWT access token for an authenticated user.

    Payload fields:
        sub      — subject (user_id, standard JWT claim)
        username — the user's display name
        iat      — issued-at timestamp (UTC)
        exp      — expiry timestamp (UTC, JWT_EXPIRE_DAYS from now)

    Args:
        user_id:  The user's UUID from the database.
        username: The user's username.

    Returns:
        A compact JWT string (header.payload.signature).
    """
    now    = datetime.now(timezone.utc)
    expiry = now + timedelta(days=JWT_EXPIRE_DAYS)

    payload: Dict[str, Any] = {
        "sub":      user_id,       # standard JWT subject claim
        "username": username,
        "iat":      now,           # issued at
        "exp":      expiry,        # expiration
    }

    token = pyjwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.debug(f"JWT created for user '{username}' (expires {expiry.date()})")
    return token


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT token entirely locally.

    Verifications performed:
        - Signature integrity (HS256 HMAC with secret key)
        - Token expiry (exp claim)
        - Issued-at sanity (iat claim)

    Args:
        token: The raw JWT string from the Authorization header.

    Returns:
        The decoded payload dict if valid, or None if invalid/expired.

    Note:
        Returns None instead of raising so callers can produce HTTP 401
        cleanly via the dependency injection layer.
    """
    try:
        payload = pyjwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload

    except pyjwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None

    except pyjwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected JWT decode error: {e}")
        return None


def extract_user_id(token: str) -> Optional[str]:
    """
    Convenience: decode a token and return only the user_id (sub claim).

    Returns None if the token is invalid or expired.
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None
