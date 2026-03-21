# models/ — Pydantic request/response models for API bodies.
from typing import List, Literal

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language question",
    )
    conversation_history: List[ConversationMessage] = Field(
        default_factory=list,
        max_length=20,
        description="Recent messages in this session for context (last N turns).",
    )
    session_id: str | None = Field(
        default=None,
        description="If provided, user and assistant messages are persisted to this session in PostgreSQL.",
    )
