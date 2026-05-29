"""
utils/helpers.py — ResQAI Shared Utility Functions
===================================================
Reusable helpers for ID generation, text truncation,
timestamp formatting, and other common operations.
"""

import uuid
import re
from datetime import datetime, timezone
from typing import List


def generate_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())


def utc_now_iso() -> str:
    """Return the current UTC timestamp as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def truncate_text(text: str, max_chars: int) -> str:
    """
    Truncate text to at most max_chars characters.
    Appends '...' if truncation occurred.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."


def generate_chat_title(query: str, max_words: int = 8) -> str:
    """
    Generate a short chat title from the first query.
    Takes the first max_words words and capitalizes them.

    Example:
        "snake bite what to do" → "Snake Bite What To Do"
    """
    words = query.strip().split()[:max_words]
    title = " ".join(words).title()
    return title if title else "New Chat"


def sanitize_query(query: str) -> str:
    """
    Basic sanitization: strip leading/trailing whitespace,
    collapse multiple spaces, remove control characters.
    """
    query = query.strip()
    query = re.sub(r"\s+", " ", query)
    query = re.sub(r"[\x00-\x1f\x7f]", "", query)   # strip control chars
    return query


def format_sources(metadata_list: List[dict]) -> List[dict]:
    """
    Format retrieved metadata entries into a clean sources list
    suitable for the API response.

    Args:
        metadata_list: List of metadata dicts from the FAISS retrieval.

    Returns:
        List of simplified source dicts.
    """
    sources = []
    for meta in metadata_list:
        sources.append({
            "id":       meta.get("id", "unknown"),
            "title":    meta.get("title", "Unknown"),
            "category": meta.get("category", "unknown"),
            "priority": meta.get("priority", "unknown"),
            "source":   meta.get("source", "unknown"),
        })
    return sources
