"""
auth/password_handler.py — Secure Offline Password Hashing
===========================================================
Uses bcrypt for password hashing and verification.

Why bcrypt?
  - Intentionally slow (adaptive cost factor) — defeats brute force
  - Automatically salts each hash — defeats rainbow tables
  - Works 100% offline — pure Python, no internet required
  - Industry standard for password storage (Django, Flask, FastAPI all use it)

NEVER store plain-text passwords. NEVER log passwords.
"""

import bcrypt

try:
    from config import BCRYPT_ROUNDS
    from utils.logger import get_logger
except ImportError:
    BCRYPT_ROUNDS = 12
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password using bcrypt.

    Process:
        1. Encode the password as UTF-8 bytes.
        2. Generate a cryptographically random salt (built into bcrypt).
        3. Run the bcrypt KDF with BCRYPT_ROUNDS cost factor.
        4. Return the full hash string (includes salt + cost embedded).

    Args:
        plain_password: The raw password string from the user.

    Returns:
        A bcrypt hash string (60 chars, starts with '$2b$').
        Safe to store directly in SQLite.

    Example output:
        "$2b$12$LnBz1RdCWoKBT/..."
    """
    if not plain_password:
        raise ValueError("Password cannot be empty")

    # bcrypt.hashpw expects bytes
    password_bytes = plain_password.encode("utf-8")
    salt           = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed         = bcrypt.hashpw(password_bytes, salt)

    # Return as string for SQLite storage
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a stored bcrypt hash.

    Process:
        1. Encode both to bytes.
        2. bcrypt.checkpw extracts the salt from the stored hash,
           re-hashes the candidate, and compares in constant time.
        3. Returns True only if they match.

    Args:
        plain_password:  The password the user just typed.
        hashed_password: The stored bcrypt hash from the database.

    Returns:
        True if passwords match, False otherwise.

    Security:
        Uses constant-time comparison internally — immune to timing attacks.
    """
    if not plain_password or not hashed_password:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception as e:
        logger.warning(f"Password verification error: {e}")
        return False
