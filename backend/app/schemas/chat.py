"""Request/response models for ``POST /api/chat`` (docs/05 §6.1)."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CompanionMode
from app.schemas.trace import AgentTrace


class ChatRequest(BaseModel):
    user_id: str = "demo_user"
    message: str = Field(min_length=1, max_length=4000)
    mode: CompanionMode = CompanionMode.role_first
    voice_enabled: bool = False
    sensor_preset_id: Optional[str] = None
    # User-chosen companion name. When unset, the backend uses the neutral
    # fallback. The persistent source of truth is UserProfile / onboarding (#21).
    companion_display_name: Optional[str] = None

    @field_validator("message")
    @classmethod
    def _message_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("message must not be blank")
        return stripped


class ChatResponse(BaseModel):
    turn_id: str
    response_text: str
    audio_url: Optional[str] = None
    agent_trace: AgentTrace
