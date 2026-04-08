"""Models for Saulo v2 chat module."""
from pydantic import BaseModel
from typing import Optional, List


class MessageCreate(BaseModel):
    """Message creation request."""
    content: str
    model: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response."""
    conversation_id: str
    text: str
    intent: str
    model_used: str


class Conversation(BaseModel):
    """Conversation model."""
    id: str
    user_id: str
    title: str
    created_at: str