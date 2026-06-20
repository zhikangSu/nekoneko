"""Sensor / StateEvent / Guardian schemas (issues #22, #12).

The boundary is explicit: raw/mock signal → SensorAdapter → StateEvent →
GuardianAgent. Guardian consumes StateEvent, never raw values, and never makes a
medical claim from a sensor preset (AGENTS.md §11).
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RawSignal(BaseModel):
    """Mock wearable / behavioral signal. Defaults represent a normal day."""

    sleep_duration_hours: float = 7.5
    steps_last_3h: int = 600
    heart_rate_current: int = 72
    heart_rate_baseline: int = 70
    last_interaction_hours: float = 1.0
    medication_overdue_minutes: int = 0
    self_reported_mood: Optional[str] = None  # e.g. "low" | "ok" | "good"


class StateEventType(str, Enum):
    NORMAL_DAY = "NORMAL_DAY"
    POOR_SLEEP = "POOR_SLEEP"
    LOW_ACTIVITY = "LOW_ACTIVITY"
    REMINDER_OVERDUE = "REMINDER_OVERDUE"
    LONG_NO_RESPONSE = "LONG_NO_RESPONSE"
    LOW_MOOD_SELF_REPORT = "LOW_MOOD_SELF_REPORT"
    PHYSIOLOGICAL_ANOMALY_MOCK = "PHYSIOLOGICAL_ANOMALY_MOCK"


class Severity(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"


class StateEvent(BaseModel):
    event_type: StateEventType
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    suggested_action: str
    medical_claim_allowed: bool = False
    source: str = "mock_sensor"
    timestamp: str


class SensorPreset(BaseModel):
    id: str
    label: str
    description: str
    raw_signal: RawSignal


class GuardianDecisionType(str, Enum):
    check_in = "check_in"
    defer = "defer"
    silent_log = "silent_log"
    safety_escalation = "safety_escalation"


class GuardianDecision(BaseModel):
    decision: GuardianDecisionType
    care_proposal: str  # the proactive message, or "" when not surfacing now
    restraint_critique: str
    reason: str
    cooldown_applied: bool
    cooldown_minutes: int
    trace_visible_summary: str


class ApplyPresetRequest(BaseModel):
    user_id: str = "demo_user"
    preset_id: str


class RefuseRequest(BaseModel):
    user_id: str = "demo_user"
    event_type: StateEventType


class ApplyPresetResponse(BaseModel):
    turn_id: str
    raw_signal: RawSignal
    state_event: StateEvent
    guardian_decision: GuardianDecision
    response_text: str  # the proactive message, or "" when Guardian stays silent
    agent_trace: "AgentTrace"


# Resolve the forward reference to AgentTrace.
from app.schemas.trace import AgentTrace  # noqa: E402

ApplyPresetResponse.model_rebuild()
