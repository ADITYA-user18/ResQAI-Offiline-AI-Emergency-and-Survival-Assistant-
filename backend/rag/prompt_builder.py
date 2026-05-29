"""
rag/prompt_builder.py — Emergency Prompt Builder
================================================
Constructs the final prompt sent to Ollama, combining:
  - System instructions (safety-focused emergency assistant persona)
  - Retrieved context chunks from FAISS
  - Recent conversation history (from SQLite)
  - The user's current question

Prompt structure:
    [SYSTEM INSTRUCTIONS]
    ---
    [RETRIEVED CONTEXT]
    ---
    [CONVERSATION HISTORY]
    ---
    [USER QUESTION]

This separation ensures the LLM clearly distinguishes between
context (what it knows) and the question (what it must answer).
"""

from typing import List, Dict, Any

try:
    from config import SYSTEM_PROMPT
    from rag.retriever import RetrievedChunk, build_context_text
    from utils.logger import get_logger
except ImportError:
    SYSTEM_PROMPT = "You are an emergency assistant. Use only the context provided."
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


def build_prompt(
    query:           str,
    chunks:          List[RetrievedChunk],
    chat_history:    List[Dict[str, Any]] = None,
    max_context_chars: int = 3000,
) -> str:
    """
    Build the complete prompt string to send to Ollama.

    Args:
        query:             The current user question.
        chunks:            Retrieved knowledge chunks from FAISS.
        chat_history:      Recent messages from SQLite (role + content dicts).
                           Format: [{"role": "user", "content": "..."}, ...]
        max_context_chars: Max characters for the context block.

    Returns:
        A fully formatted prompt string ready for Ollama.
    """
    chat_history = chat_history or []

    sections = []

    # ── Section 1: System Instructions ────────────────────────────────────────
    sections.append(SYSTEM_PROMPT.strip())
    sections.append("=" * 60)

    # ── Section 2: Retrieved Context ──────────────────────────────────────────
    if chunks:
        context_text = "\n".join([f"- {c.text}" for c in chunks])
        sections.append("<context>")
        sections.append(context_text)
        sections.append("</context>")
        sections.append("\n")
    else:
        sections.append(
            "There is no locally stored information for this query. Answer using general emergency principles.\n"
        )

    # ── Section 3: Recent Conversation History ────────────────────────────────
    if chat_history:
        sections.append("CONVERSATION HISTORY (for context):")
        sections.append("-" * 40)
        for msg in chat_history:
            role    = msg.get("role", "user").upper()
            content = msg.get("content", "").strip()
            sections.append(f"{role}: {content}")
        sections.append("=" * 60)

    # ── Section 4: Current Question ───────────────────────────────────────────
    sections.append(f"QUESTION: {query.strip()}\n")
    sections.append("ANSWER:")

    prompt = "\n".join(sections)

    logger.debug(
        f"Prompt built: {len(chunks)} chunks, "
        f"{len(chat_history)} history msgs, "
        f"{len(prompt)} total chars"
    )
    return prompt


def build_system_prompt() -> str:
    """Return the system prompt string (used as Ollama's 'system' field)."""
    return SYSTEM_PROMPT.strip()
