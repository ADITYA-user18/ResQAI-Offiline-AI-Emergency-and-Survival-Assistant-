"""
database/chat_db.py — ResQAI SQLite Database (Users + Chats + Messages)
========================================================================
Handles ALL local storage:
  users    — one row per registered account (auth, NOT embeddings)
  chats    — one row per conversation session (linked to a user)
  messages — one row per user/assistant message turn (linked to a chat)

Two-system rule (unchanged):
  FAISS / embeddings   → knowledge/embeddings/ (READ-ONLY, never touched here)
  SQLite               → this file only (users, chats, messages)
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    from config import SQLITE_DB_PATH
    from utils.logger import get_logger
except ImportError:
    SQLITE_DB_PATH = Path("database/resqai_chats.db")
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# DATABASE INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def init_database() -> None:
    """
    Create all tables if they do not yet exist. Safe to call on every startup.

    Tables:
        users    — local user accounts (offline auth)
        chats    — session metadata, owned by a user
        messages — individual message turns, linked to a chat
    """
    SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _get_connection() as conn:
        cursor = conn.cursor()

        # ── users table ────────────────────────────────────────────────────────
        # Stores local accounts only. No cloud, no OAuth.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id       TEXT PRIMARY KEY,
                username      TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at    TEXT NOT NULL,
                last_login    TEXT,
                device_id     TEXT
            )
        """)

        # ── chats table ────────────────────────────────────────────────────────
        # user_id links every chat to its owner.
        # A user can ONLY retrieve chats WHERE user_id = their own user_id.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id    TEXT PRIMARY KEY,
                user_id    TEXT NOT NULL,
                title      TEXT NOT NULL DEFAULT 'New Chat',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)

        # ── messages table ─────────────────────────────────────────────────────
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id   TEXT PRIMARY KEY,
                chat_id      TEXT NOT NULL,
                role         TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content      TEXT NOT NULL,
                created_at   TEXT NOT NULL,
                FOREIGN KEY  (chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
            )
        """)

        # ── Indexes ────────────────────────────────────────────────────────────
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_username
            ON users (username)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chats_user_id
            ON chats (user_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chats_updated_at
            ON chats (updated_at DESC)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_chat_id
            ON messages (chat_id)
        """)

        conn.commit()

    logger.info(f"SQLite database initialized at: {SQLITE_DB_PATH}")


# ─────────────────────────────────────────────────────────────────────────────
# CONNECTION CONTEXT MANAGER
# ─────────────────────────────────────────────────────────────────────────────

@contextmanager
def _get_connection():
    """Yield a SQLite connection with WAL mode and row_factory set."""
    conn = sqlite3.connect(str(SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row          # enables dict-like row access
    conn.execute("PRAGMA journal_mode=WAL") # better concurrent read performance
    conn.execute("PRAGMA foreign_keys=ON")  # enforce FK + CASCADE constraints
    try:
        yield conn
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# USER OPERATIONS  (offline auth — no cloud)
# ─────────────────────────────────────────────────────────────────────────────

def create_user(
    user_id:       str,
    username:      str,
    password_hash: str,
    device_id:     Optional[str] = None,
) -> Dict[str, Any]:
    """
    Insert a new user account row.

    Args:
        user_id:       UUID4 string for the new account.
        username:      Case-insensitive unique username.
        password_hash: bcrypt hash (NEVER store plain passwords).
        device_id:     Optional device identifier for multi-device tracking.

    Returns:
        Dict with user metadata (no password_hash included).

    Raises:
        sqlite3.IntegrityError: If username already exists (UNIQUE constraint).
    """
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username, password_hash, created_at, device_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, username.lower(), password_hash, now, device_id),
        )
        conn.commit()
    logger.info(f"New user created: '{username}' ({user_id})")
    return {
        "user_id":    user_id,
        "username":   username.lower(),
        "created_at": now,
        "last_login": None,
        "device_id":  device_id,
    }


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Return a user row by username (case-insensitive), or None.
    Includes password_hash for login verification.
    """
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
            (username.lower(),),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Return a user row by user_id, or None. Excludes password_hash."""
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT user_id, username, created_at, last_login, device_id
            FROM users WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def username_exists(username: str) -> bool:
    """Return True if username is already taken (case-insensitive)."""
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE",
            (username.lower(),),
        ).fetchone()
    return row is not None


def update_last_login(user_id: str) -> None:
    """Update the last_login timestamp for a user (called on successful login)."""
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            "UPDATE users SET last_login = ? WHERE user_id = ?",
            (now, user_id),
        )
        conn.commit()
    logger.debug(f"Updated last_login for user {user_id}")


# ─────────────────────────────────────────────────────────────────────────────
# CHAT (SESSION) OPERATIONS  — all scoped to a user_id
# ─────────────────────────────────────────────────────────────────────────────

def create_chat(chat_id: str, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
    """
    Insert a new chat session row owned by a specific user.

    Args:
        chat_id:  UUID string for the new session.
        user_id:  UUID of the owning user.
        title:    Human-readable title (auto-generated from first query).

    Returns:
        Dict with the new chat's metadata.
    """
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO chats (chat_id, user_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (chat_id, user_id, title, now, now),
        )
        conn.commit()
    logger.debug(f"Created chat: {chat_id} for user {user_id} — '{title}'")
    return {
        "chat_id":    chat_id,
        "user_id":    user_id,
        "title":      title,
        "created_at": now,
        "updated_at": now,
    }


def get_chats_for_user(user_id: str) -> List[Dict[str, Any]]:
    """
    Return all chat sessions owned by user_id, newest first.

    SECURITY: This query ALWAYS filters by user_id — a user can
    never see another user's chats.
    """
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT chat_id, user_id, title, created_at, updated_at
            FROM chats
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_chat_by_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """Return a single chat session's metadata, or None if not found."""
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT chat_id, user_id, title, created_at, updated_at
            FROM chats WHERE chat_id = ?
            """,
            (chat_id,),
        ).fetchone()
    return dict(row) if row else None


def get_chat_for_user(chat_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Return a chat ONLY if it belongs to user_id.

    SECURITY: The dual filter (chat_id AND user_id) prevents IDOR attacks
    where a user guesses another user's chat UUID.
    """
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT chat_id, user_id, title, created_at, updated_at
            FROM chats
            WHERE chat_id = ? AND user_id = ?
            """,
            (chat_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def chat_exists_for_user(chat_id: str, user_id: str) -> bool:
    """Return True if the chat exists AND belongs to this user."""
    return get_chat_for_user(chat_id, user_id) is not None


def update_chat_timestamp(chat_id: str) -> None:
    """Update the updated_at field of a chat (called after each new message)."""
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            "UPDATE chats SET updated_at = ? WHERE chat_id = ?",
            (now, chat_id),
        )
        conn.commit()


def update_chat_title(chat_id: str, title: str) -> None:
    """Update the title of a chat session."""
    with _get_connection() as conn:
        conn.execute(
            "UPDATE chats SET title = ? WHERE chat_id = ?",
            (title, chat_id),
        )
        conn.commit()


def delete_chat_for_user(chat_id: str, user_id: str) -> bool:
    """
    Delete a chat and all its messages, only if it belongs to user_id.

    SECURITY: Dual filter prevents deleting another user's chat.

    Returns:
        True if deleted, False if not found or not owned by this user.
    """
    with _get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM chats WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        )
        conn.commit()
    deleted = cursor.rowcount > 0
    if deleted:
        logger.info(f"Deleted chat {chat_id} for user {user_id}")
    return deleted


# ─────────────────────────────────────────────────────────────────────────────
# MESSAGE OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def save_message(
    message_id: str,
    chat_id:    str,
    role:       str,
    content:    str,
) -> Dict[str, Any]:
    """
    Persist a single message to the messages table.

    Args:
        message_id: UUID for this message.
        chat_id:    Parent chat session UUID.
        role:       'user' or 'assistant'.
        content:    The message text.

    Returns:
        Dict with all message fields.
    """
    now = _utc_now()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (message_id, chat_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, chat_id, role, content, now),
        )
        conn.commit()
    logger.debug(f"Saved {role} message to chat {chat_id}")
    return {
        "message_id": message_id,
        "chat_id":    chat_id,
        "role":       role,
        "content":    content,
        "created_at": now,
    }


def get_messages_by_chat(chat_id: str) -> List[Dict[str, Any]]:
    """Return all messages for a given chat, ordered chronologically."""
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT message_id, chat_id, role, content, created_at
            FROM messages
            WHERE chat_id = ?
            ORDER BY created_at ASC
            """,
            (chat_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_recent_messages(chat_id: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Return the most recent `limit` messages for conversation context.
    Returns in chronological order (oldest first) for prompt building.
    """
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT message_id, chat_id, role, content, created_at
            FROM messages
            WHERE chat_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (chat_id, limit),
        ).fetchall()
    # Reverse so oldest-first (correct conversation order for prompt)
    return [dict(row) for row in reversed(rows)]


# ─────────────────────────────────────────────────────────────────────────────
# PRIVATE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _utc_now() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
