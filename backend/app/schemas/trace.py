"""Agent trace schema.

Every ``/api/chat`` response includes an ``AgentTrace`` even in demo mode
(AGENTS.md §13). The trace keeps the Agent / Tool / Guard / StateEvent /
Retrieval / Memory distinction visible (AGENTS.md §5). Slice 1 emits a minimal
baseline trace; #9 will expand persistence and the Trace Panel.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from app.core.constants import CompanionMode, RiskLevel, Route, TraceEntryKind


class TraceStep(BaseModel):
    """One step in the trace, tagged with its ``kind`` so the UI can label it."""

    kind: TraceEntryKind
    name: str
    summary: str = ""
    detail: dict[str, Any] = Field(default_factory=dict)


class AgentTrace(BaseModel):
    turn_id: str
    mode: CompanionMode
    route: Route
    risk_level: RiskLevel
    agents: list[TraceStep] = Field(default_factory=list)
    tools: list[TraceStep] = Field(default_factory=list)
    guards: list[TraceStep] = Field(default_factory=list)
    state_event: Optional[TraceStep] = None
    memory_used: bool = False
    retrieval_used: bool = False
    safety_critic_used: bool = False


class TraceRecord(BaseModel):
    """A persisted trace: the per-turn AgentTrace plus who/when (issue #9)."""

    turn_id: str
    user_id: str
    created_at: str  # ISO-8601 UTC
    trace: AgentTrace


class TraceSummary(BaseModel):
    """Compact row for the trace history list."""

    turn_id: str
    user_id: str
    created_at: str
    route: Route
    risk_level: RiskLevel
    safety_critic_used: bool = False
    retrieval_used: bool = False
