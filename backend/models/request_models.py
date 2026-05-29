"""
models/request_models.py — FastAPI Request Pydantic Models
===========================================================
Input validation models for all API endpoints.
Pydantic automatically validates types, lengths, and required fields.
"""

import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

try:
    from config import USERNAME_MIN_LEN, USERNAME_MAX_LEN, PASSWORD_MIN_LEN
except ImportError:
    USERNAME_MIN_LEN = 3
    USERNAME_MAX_LEN = 30
    PASSWORD_MIN_LEN = 6

# ─────────────────────────────────────────────────────────────────────────────
# AUTH REQUEST MODELS
# ─────────────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    """Request body for POST /signup"""
    username: str = Field(
        ...,
        min_length=USERNAME_MIN_LEN,
        max_length=USERNAME_MAX_LEN,
        description="Unique username (3–30 chars, alphanumeric + underscore)",
        examples=["aditya"],
    )
    password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LEN,
        description="Password (minimum 6 characters)",
        examples=["secure_password"],
    )
    device_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional device identifier for tracking sessions",
        examples=["android-device-001"],
    )

    @field_validator("username")
    @classmethod
    def username_must_be_valid(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username may only contain letters, numbers, and underscores"
            )
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Password cannot be blank")
        return v


class LoginRequest(BaseModel):
    """Request body for POST /login"""
    username: str = Field(
        ...,
        min_length=1,
        max_length=USERNAME_MAX_LEN,
        description="Your registered username",
        examples=["aditya"],
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Your password",
        examples=["secure_password"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# CHAT REQUEST MODELS
# ─────────────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    """
    Request body for POST /ask

    Fields:
        chat_id: Optional existing chat UUID. If omitted, a new chat is created.
        query:   The user's emergency question (required, 1–2000 chars).
    """
    chat_id: Optional[str] = Field(
        default=None,
        description="Existing chat session UUID. Omit to start a new conversation.",
        examples=["3f8c1a2b-4d5e-4f6a-8b9c-0d1e2f3a4b5c"],
    )
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The emergency question to ask.",
        examples=["What should I do for a snake bite?"],
    )

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be blank or whitespace only")
        return v.strip()


class NewChatRequest(BaseModel):
    """Optional request body for POST /new-chat"""
    title: Optional[str] = Field(
        default="New Chat",
        max_length=200,
        description="Custom title for the new chat session.",
        examples=["Snake Bite Emergency"],
    )
