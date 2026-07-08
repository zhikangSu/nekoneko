"""Short-term conversation history schemas (#82)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """One bounded, short-term chat message kept in process memory only."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1200)
