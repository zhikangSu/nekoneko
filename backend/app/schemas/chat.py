"""Request/response models for ``POST /api/chat`` (docs/05 §6.1)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

from app.core.constants import CompanionMode
from app.schemas.conversation import ConversationMessage
from app.schemas.relationship import (
    ElderControlAction,
    MaterialType,
    RoleCueMessage,
    RoleId,
    RoleSelectionMode,
    StudyCondition,
)
from app.schemas.trace import AgentTrace

MemoryScope = Literal["default", "session_only"]


class ChatRequest(BaseModel):
    user_id: str = "demo_user"
    message: str = Field(min_length=1, max_length=4000)
    mode: CompanionMode = CompanionMode.role_first
    voice_enabled: bool = False
    sensor_preset_id: Optional[str] = None
    # User-chosen companion name. When unset, the backend uses the neutral
    # fallback. The persistent source of truth is UserProfile / onboarding (#21).
    companion_display_name: Optional[str] = None
    # Relationship role controls for #73. Defaults keep the existing automatic
    # orchestration behavior unchanged.
    role_selection_mode: RoleSelectionMode = RoleSelectionMode.auto
    selected_role_ids: list[RoleId] = Field(default_factory=list)
    # Optional Study-1 topic/material anchor for the relationship-aware demo
    # (#83). The backend records only compact metadata in trace.
    topic_id: Optional[str] = Field(default=None, max_length=32)
    topic_label: Optional[str] = Field(default=None, max_length=80)
    material_type: Optional[MaterialType] = None
    study_condition: StudyCondition = StudyCondition.c3_relationship_aware
    study_session_id: Optional[str] = Field(default=None, max_length=64)
    elder_control_action: ElderControlAction = ElderControlAction.continue_session
    # Some UI surfaces, such as the ambient social-cue scene, should keep their
    # short-term continuity without reading/writing the user's durable memory.
    memory_scope: MemoryScope = "default"
    # UI-only opening lines that were already shown before the first API turn.
    # They seed bounded, in-process history only when the session is empty.
    conversation_seed: list[ConversationMessage] = Field(
        default_factory=list,
        max_length=4,
    )
    # Relationship roles already visible in the current UI scene. This is
    # conversational context, not a manual role choice by the user.
    context_role_ids: list[RoleId] = Field(default_factory=list, max_length=3)

    @field_validator("message")
    @classmethod
    def _message_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("message must not be blank")
        return stripped

    @field_validator("topic_id", "topic_label")
    @classmethod
    def _optional_text_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None

    @field_validator("study_session_id")
    @classmethod
    def _optional_session_not_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ChatResponse(BaseModel):
    turn_id: str
    response_text: str
    role_messages: list[RoleCueMessage] = Field(default_factory=list)
    audio_url: Optional[str] = None
    agent_trace: AgentTrace
