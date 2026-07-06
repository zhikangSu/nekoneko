"""Memory models (issue #10).

Three memory kinds: preferences, events, and reminder/setting notes. The
companion's display name is NOT memory here — that lives in UserProfile (#21).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class MemoryCategory(str, Enum):
    profile_preference = "profile_preference"
    event_memory = "event_memory"
    reminder_or_setting = "reminder_or_setting"
    boundary_preference = "boundary_preference"


class MemoryEntry(BaseModel):
    id: str
    user_id: str
    category: MemoryCategory
    content: str
    created_at: str


class MemoryCreate(BaseModel):
    category: MemoryCategory = MemoryCategory.event_memory
    content: str = Field(min_length=1, max_length=500)

    @field_validator("content")
    @classmethod
    def _content_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("content must not be blank")
        return stripped


class MemorySettings(BaseModel):
    extraction_paused: bool = False


class MemorySettingsUpdate(BaseModel):
    extraction_paused: Optional[bool] = None


class MemoryView(BaseModel):
    """GET /api/memory/{user_id} response."""

    user_id: str
    settings: MemorySettings
    memories: list[MemoryEntry]
