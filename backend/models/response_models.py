"""
models/response_models.py — FastAPI Response Pydantic Models
=============================================================
Structured response schemas for all API endpoints.
Ensures consistent JSON output for web browser clients.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# AUTH RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────────────────

class UserPublicModel(BaseModel):
    """Public user info — NEVER includes password_hash."""
    user_id:    str
    username:   str
    created_at: str
    last_login: Optional[str] = None
    device_id:  Optional[str] = None


class AuthResponse(BaseModel):
    """
    Response from POST /signup and POST /login.
    The access_token is the JWT the client must store and send on every request.
    """
    access_token: str = Field(..., description="JWT Bearer token")
    token_type:   str = Field(default="Bearer")
    user:         UserPublicModel


class MeResponse(BaseModel):
    """Response from GET /me — returns current authenticated user's info."""
    user: UserPublicModel


class LogoutResponse(BaseModel):
    """Response from POST /logout"""
    success: bool
    message: str


# ─────────────────────────────────────────────────────────────────────────────
# SHARED CHAT MODELS
# ─────────────────────────────────────────────────────────────────────────────

class SourceModel(BaseModel):
    """Represents a single knowledge source cited in an answer."""
    id:       str
    title:    str
    category: str
    priority: str
    source:   str


class MessageModel(BaseModel):
    """A single chat message (user or assistant)."""
    message_id: str
    chat_id:    str
    role:       str
    content:    str
    created_at: str


class ChatModel(BaseModel):
    """A chat session (without messages). Includes user_id for ownership."""
    chat_id:    str
    user_id:    str
    title:      str
    created_at: str
    updated_at: str


# ─────────────────────────────────────────────────────────────────────────────
# /ask RESPONSE
# ─────────────────────────────────────────────────────────────────────────────

class ChunkModel(BaseModel):
    """A single retrieved knowledge chunk."""
    chunk_id:  str
    title:     str
    category:  str
    priority:  str
    source:    str
    text:      str
    distance:  float


class AskResponse(BaseModel):
    """Response from POST /ask"""
    chat_id:          str
    answer:           str
    sources:          List[SourceModel]
    retrieved_chunks: List[ChunkModel]


# ─────────────────────────────────────────────────────────────────────────────
# CHAT ROUTE RESPONSES
# ─────────────────────────────────────────────────────────────────────────────

class NewChatResponse(BaseModel):
    """Response from POST /new-chat"""
    chat_id:    str
    user_id:    str
    title:      str
    created_at: str
    updated_at: str


class AllChatsResponse(BaseModel):
    """Response from GET /chats"""
    total: int
    chats: List[ChatModel]


class ConversationResponse(BaseModel):
    """Response from GET /chat/{chat_id}"""
    chat:     ChatModel
    messages: List[MessageModel]


class DeleteChatResponse(BaseModel):
    """Response from DELETE /chat/{chat_id}"""
    success: bool
    message: str
    chat_id: str


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM RESPONSES
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response from GET /health"""
    status:           str
    faiss_loaded:     bool
    knowledge_loaded: bool
    ollama_available: bool
    model:            str
    vector_count:     int
    chunk_count:      int
    database:         str


class RootResponse(BaseModel):
    """Response from GET /"""
    app:     str
    version: str
    status:  str
    docs:    str
