"""Privacy-preserving caregiver dashboard models (issue #79).

The caregiver surface is a mock research/demo view. It exposes aggregate
status and event metadata, not full chat transcripts or sensitive memory text.
"""

from __future__ import annotations

from app.core.constants import RiskLevel, Route
from app.schemas.reminder import Recurrence

from pydantic import BaseModel, Field


class CaregiverReminderDigest(BaseModel):
    reminder_id: str
    label: str
    time: str
    recurrence: Recurrence
    status: str
    last_confirmed_at: str | None = None


class CaregiverEventDigest(BaseModel):
    turn_id: str
    created_at: str
    route: Route
    risk_level: RiskLevel
    summary: str


class CaregiverSummary(BaseModel):
    user_id: str
    generated_at: str
    active_reminders: int = 0
    confirmed_reminders_today: int = 0
    pending_reminders: int = 0
    proactive_events_7d: int = 0
    safety_events_7d: int = 0
    reminders: list[CaregiverReminderDigest] = Field(default_factory=list)
    proactive_events: list[CaregiverEventDigest] = Field(default_factory=list)
    safety_events: list[CaregiverEventDigest] = Field(default_factory=list)
    privacy_boundaries: list[str] = Field(default_factory=list)
