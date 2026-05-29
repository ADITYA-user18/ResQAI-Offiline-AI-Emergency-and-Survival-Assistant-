"""
routes/chat_routes.py — Chat Session & History API (Authenticated)
===================================================================
All chat CRUD operations are now protected by JWT and scoped per user.

SECURITY: Every route uses current_user.user_id to filter data.
A user cannot read, modify, or delete another user's chats.

Endpoints:
  POST   /new-chat           — Create a new chat (owned by the caller)
  GET    /chats              — List THIS user's chats only
  GET    /chat/{chat_id}     — Get THIS user's conversation by chat_id
  DELETE /chat/{chat_id}     — Delete THIS user's chat
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

try:
    from models.request_models  import NewChatRequest
    from models.response_models import (
        NewChatResponse,
        AllChatsResponse,
        ChatModel,
        ConversationResponse,
        MessageModel,
        DeleteChatResponse,
    )
    from services.chat_service import chat_service
    from auth.auth_handler     import AuthDep
    from utils.logger          import get_logger
except ImportError as e:
    raise ImportError(f"chat_routes import error: {e}")

logger = get_logger(__name__)
router = APIRouter(tags=["Chat"])


# ─────────────────────────────────────────────────────────────────────────────
# POST /new-chat — Create a new chat session for the current user
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/new-chat",
    response_model=NewChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
    description=(
        "Creates a new empty chat session owned by the authenticated user. "
        "Requires JWT in Authorization header."
    ),
)
async def new_chat(
    current_user: AuthDep,
    request: NewChatRequest = None,
) -> NewChatResponse:
    """Create a new chat session owned by the current user."""
    title = (request.title if request and request.title else "New Chat")
    chat  = chat_service.create_new_chat(user_id=current_user.user_id, title=title)
    logger.info(f"[/new-chat] Created {chat['chat_id']} for user '{current_user.username}'")
    return NewChatResponse(**chat)


# ─────────────────────────────────────────────────────────────────────────────
# GET /chats — List only THIS user's chats
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/chats",
    response_model=AllChatsResponse,
    summary="List your chat sessions",
    description=(
        "Returns only YOUR chat sessions, ordered by most recently updated. "
        "Other users' chats are never returned."
    ),
)
async def get_all_chats(current_user: AuthDep) -> AllChatsResponse:
    """Return all chat sessions belonging to the current user."""
    chats = chat_service.get_all_chats(user_id=current_user.user_id)
    logger.debug(
        f"[/chats] Returning {len(chats)} chats for user '{current_user.username}'"
    )
    return AllChatsResponse(
        total=len(chats),
        chats=[ChatModel(**c) for c in chats],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /chat/{chat_id} — Get full conversation (ownership verified)
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/chat/{chat_id}",
    response_model=ConversationResponse,
    summary="Get a conversation by ID",
    description=(
        "Returns the chat session and all messages. "
        "Returns 404 if the chat does not exist or belongs to another user."
    ),
)
async def get_conversation(chat_id: str, current_user: AuthDep) -> ConversationResponse:
    """
    Return full conversation (metadata + all messages).
    404 is returned for both 'not found' and 'belongs to another user'
    to prevent information leakage about other users' chat IDs.
    """
    try:
        data = chat_service.get_conversation(
            chat_id=chat_id,
            user_id=current_user.user_id,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat not found: {chat_id}",
        )

    logger.debug(
        f"[/chat/{chat_id}] Returning {len(data['messages'])} messages "
        f"for user '{current_user.username}'"
    )

    return ConversationResponse(
        chat=ChatModel(**data["chat"]),
        messages=[MessageModel(**m) for m in data["messages"]],
    )


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /chat/{chat_id} — Delete (ownership verified)
# ─────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/chat/{chat_id}",
    response_model=DeleteChatResponse,
    summary="Delete a chat session",
    description=(
        "Permanently deletes the chat and all its messages. "
        "Returns 404 if the chat does not exist or belongs to another user."
    ),
)
async def delete_chat(chat_id: str, current_user: AuthDep) -> DeleteChatResponse:
    """Delete a chat only if it belongs to the current user."""
    deleted = chat_service.delete_chat(
        chat_id=chat_id,
        user_id=current_user.user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat not found: {chat_id}",
        )

    logger.info(
        f"[DELETE /chat/{chat_id}] Deleted by user '{current_user.username}'"
    )
    return DeleteChatResponse(
        success=True,
        message="Chat deleted successfully.",
        chat_id=chat_id,
    )

# ─────────────────────────────────────────────────────────────────────────────
# PATCH /chat/{chat_id}/title — Rename Chat
# ─────────────────────────────────────────────────────────────────────────────

class RenameChatRequest(BaseModel):
    title: str

@router.patch(
    "/chat/{chat_id}/title",
    summary="Rename a chat session",
    description="Renames a chat session. Returns 404 if not found or unauthorized.",
)
async def rename_chat(chat_id: str, request: RenameChatRequest, current_user: AuthDep):
    success = chat_service.rename_chat(chat_id, current_user.user_id, request.title)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat not found: {chat_id}",
        )
    return {"success": True, "chat_id": chat_id, "new_title": request.title}
