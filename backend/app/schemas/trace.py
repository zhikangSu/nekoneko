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


class ResearchRoleTrace(BaseModel):
    selected_roles: list[str] = Field(default_factory=list)
    primary_role: Optional[str] = None
    role_selection_mode: Optional[str] = None
    requested_role_ids: list[str] = Field(default_factory=list)
    cueing_style: Optional[str] = None


class ResearchTopicTrace(BaseModel):
    topic_id: Optional[str] = None
    topic_label: Optional[str] = None
    material_type: Optional[str] = None
    classified_topic: Optional[str] = None


class ResearchBoundaryTrace(BaseModel):
    boundary_state: str = "none"
    boundary_notes: list[str] = Field(default_factory=list)


class ResearchInteractionTrace(BaseModel):
    intent: Optional[str] = None
    role_selection_source: Optional[str] = None
    context_role_ids: list[str] = Field(default_factory=list)


class ResearchControlTrace(BaseModel):
    study_condition: Optional[str] = None
    study_session_id: Optional[str] = None
    elder_control_action: Optional[str] = None


class ResearchTraceMetadata(BaseModel):
    interaction: ResearchInteractionTrace = Field(
        default_factory=ResearchInteractionTrace
    )
    role: ResearchRoleTrace = Field(default_factory=ResearchRoleTrace)
    topic: ResearchTopicTrace = Field(default_factory=ResearchTopicTrace)
    boundary: ResearchBoundaryTrace = Field(default_factory=ResearchBoundaryTrace)
    control: ResearchControlTrace = Field(default_factory=ResearchControlTrace)


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
    conversation_history_used: bool = False
    conversation_history_count: int = 0
    conversation_seed_used: bool = False
    conversation_seed_count: int = 0
    # Compact research/demo metadata for relationship-aware turns. Keep this
    # privacy-preserving: IDs/enums/role choices, not full sensitive content.
    research_metadata: dict[str, Any] = Field(default_factory=dict)
    research_trace: ResearchTraceMetadata = Field(default_factory=ResearchTraceMetadata)


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
