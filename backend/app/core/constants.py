"""Shared constants and enums for the companion backend.

Naming rule (AGENTS.md §4.1): the companion has no hardcoded fixed name. The
user chooses ``companion_display_name`` during onboarding; before naming, the UI
and prompts fall back to a neutral label. Never invent a fixed default name.
"""

from __future__ import annotations

from enum import Enum

# Neutral fallback used only when ``companion_display_name`` is unset.
DEFAULT_COMPANION_DISPLAY_NAME = "陪伴 AI"
COMPANION_DISPLAY_NAME_FALLBACK_BILINGUAL = "陪伴 AI / AI Companion"


class CompanionMode(str, Enum):
    """Response style. ``reminiscence_mode`` is P1 and intentionally omitted."""

    role_first = "role_first"
    neutral_assistant = "neutral_assistant"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    crisis = "crisis"


class Route(str, Enum):
    """Coordinator routes (docs/05 §11.5). Slice 1 only emits ``companion_chat``."""

    companion_chat = "companion_chat"
    reminder_management = "reminder_management"
    memory_management = "memory_management"
    proactive_checkin = "proactive_checkin"
    retrieval_supported_response = "retrieval_supported_response"
    relationship_cueing = "relationship_cueing"
    safety_response = "safety_response"
    emergency_mock = "emergency_mock"


class TraceEntryKind(str, Enum):
    """Keeps the Agent / Tool / Guard distinction visible in the trace (AGENTS.md §5)."""

    agent = "agent"
    tool = "tool"
    guard = "guard"
    state_event = "state_event"
    retrieval = "retrieval"
    memory = "memory"
