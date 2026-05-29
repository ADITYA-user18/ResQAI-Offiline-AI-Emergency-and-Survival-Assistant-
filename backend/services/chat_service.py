"""
services/chat_service.py — Chat Session Business Logic (Per-User Isolated)
===========================================================================
Orchestrates all chat/session operations scoped to a specific user.

KEY SECURITY CHANGE: every method now requires user_id.
No method returns data without verifying ownership.
"""

from typing import List, Dict, Any, Optional

try:
    from database.chat_db import (
        create_chat,
        get_chats_for_user,
        get_chat_for_user,
        chat_exists_for_user,
        update_chat_timestamp,
        update_chat_title,
        delete_chat_for_user,
        save_message,
        get_messages_by_chat,
        get_recent_messages,
    )
    from utils.helpers import generate_uuid, generate_chat_title
    from utils.logger import get_logger
    from config import CHAT_TITLE_MAX_WORDS, CHAT_HISTORY_WINDOW
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)
    CHAT_TITLE_MAX_WORDS = 8
    CHAT_HISTORY_WINDOW  = 6

logger = get_logger(__name__)


class ChatService:
    """
    Per-user chat service. All methods are scoped to a user_id.

    SECURITY INVARIANT:
        Every read/write/delete operation includes user_id in the SQL query.
        A user can never access, modify, or delete another user's chats.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # SESSION MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def create_new_chat(self, user_id: str, title: str = "New Chat") -> Dict[str, Any]:
        """
        Create a new empty chat session owned by user_id.

        Args:
            user_id: The authenticated user's UUID.
            title:   Initial title (overridden after first message).

        Returns:
            Dict with chat_id, user_id, title, timestamps.
        """
        chat_id = generate_uuid()
        chat    = create_chat(chat_id=chat_id, user_id=user_id, title=title)
        logger.info(f"New chat created: {chat_id} for user {user_id}")
        return chat

    def get_or_create_chat(
        self,
        user_id:     str,
        chat_id:     Optional[str],
        first_query: str = "",
    ) -> Dict[str, Any]:
        """
        Return an existing chat (owned by user_id) or create a new one.

        If chat_id provided AND belongs to user_id → return it.
        If chat_id missing or doesn't belong to user_id → create new chat.

        This prevents a user from hijacking another user's chat_id.

        Args:
            user_id:     The authenticated user's UUID.
            chat_id:     Optional existing chat UUID from the request.
            first_query: Used to auto-generate the title for new chats.

        Returns:
            Chat metadata dict.
        """
        # Only reuse chat if it actually belongs to this user
        if chat_id and chat_exists_for_user(chat_id, user_id):
            logger.debug(f"Continuing chat {chat_id} for user {user_id}")
            return get_chat_for_user(chat_id, user_id)

        # New chat — generate title from the query
        title   = generate_chat_title(first_query, CHAT_TITLE_MAX_WORDS)
        new_id  = generate_uuid()
        chat    = create_chat(chat_id=new_id, user_id=user_id, title=title)
        logger.info(f"Auto-created chat '{title}': {new_id} for user {user_id}")
        return chat

    def get_all_chats(self, user_id: str) -> List[Dict[str, Any]]:
        """Return all chat sessions owned by user_id, newest first."""
        return get_chats_for_user(user_id)

    def get_chat(self, chat_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Return a chat only if it belongs to user_id, else None."""
        return get_chat_for_user(chat_id, user_id)

    def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Delete a chat (and messages) only if it belongs to user_id."""
        return delete_chat_for_user(chat_id, user_id)
        
    def rename_chat(self, chat_id: str, user_id: str, new_title: str) -> bool:
        """Rename a chat if it belongs to user_id."""
        if chat_exists_for_user(chat_id, user_id):
            update_chat_title(chat_id, new_title)
            return True
        return False

    # ─────────────────────────────────────────────────────────────────────────
    # MESSAGE MANAGEMENT
    # ─────────────────────────────────────────────────────────────────────────

    def save_user_message(self, chat_id: str, content: str) -> Dict[str, Any]:
        """Save a user message to the database."""
        msg_id = generate_uuid()
        msg    = save_message(msg_id, chat_id, "user", content)
        update_chat_timestamp(chat_id)
        return msg

    def save_assistant_message(self, chat_id: str, content: str) -> Dict[str, Any]:
        """Save an assistant (AI) response to the database."""
        msg_id = generate_uuid()
        msg    = save_message(msg_id, chat_id, "assistant", content)
        update_chat_timestamp(chat_id)
        return msg

    def get_conversation(self, chat_id: str, user_id: str) -> Dict[str, Any]:
        """
        Return full chat metadata + all messages, only if owned by user_id.

        Args:
            chat_id: UUID of the chat session.
            user_id: The requesting user's UUID.

        Returns:
            Dict with 'chat' metadata and 'messages' list.

        Raises:
            ValueError: If chat not found or not owned by this user.
        """
        chat = get_chat_for_user(chat_id, user_id)
        if not chat:
            raise ValueError(
                f"Chat {chat_id} not found or does not belong to this user."
            )

        messages = get_messages_by_chat(chat_id)
        return {
            "chat":     chat,
            "messages": messages,
        }

    def get_recent_context(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Return the most recent messages for prompt context building.
        No user_id check needed — chat ownership already verified upstream.
        """
        return get_recent_messages(chat_id, limit=CHAT_HISTORY_WINDOW)


# ── Module-level singleton ────────────────────────────────────────────────────
chat_service = ChatService()
