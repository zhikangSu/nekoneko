"""Graph state shared across nodes (issue #5).

A lightweight, framework-free state object that mirrors a LangGraph state so the
runner can be swapped for real LangGraph later without changing nodes. Holds the
turn inputs plus everything the nodes accumulate (risk, route, draft, trace
steps). The trace lists keep the Agent / Tool / Guard distinction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.constants import CompanionMode, Route
from app.safety.risk_classifier import RiskClassification
from app.schemas.profile import UserProfile
from app.schemas.relationship import (
    ElderControlAction,
    MaterialType,
    RoleCueMessage,
    RoleId,
    RoleSelectionMode,
    StudyCondition,
)
from app.schemas.trace import TraceStep


@dataclass
class GraphState:
    # Inputs
    turn_id: str
    user_id: str
    user_input: str
    mode: CompanionMode
    user_profile: UserProfile
    role_selection_mode: RoleSelectionMode = RoleSelectionMode.auto
    selected_role_ids: list[RoleId] = field(default_factory=list)
    topic_id: Optional[str] = None
    topic_label: Optional[str] = None
    material_type: Optional[MaterialType] = None
    study_condition: StudyCondition = StudyCondition.c3_relationship_aware
    study_session_id: Optional[str] = None
    elder_control_action: ElderControlAction = ElderControlAction.continue_session

    # Populated by #22 / #10 / #13 later; present now so routing is stable.
    state_event: Optional[dict[str, Any]] = None
    memory_context: Optional[Any] = None
    retrieval_needed: bool = False
    retrieval_context: Optional[str] = None

    # Filled during the run
    risk: RiskClassification = field(default_factory=RiskClassification)
    route: Optional[Route] = None
    draft_reply: str = ""
    response_text: str = ""

    # Result flags (mirror AgentTrace)
    memory_used: bool = False
    retrieval_used: bool = False
    safety_critic_used: bool = False
    role_messages: list[RoleCueMessage] = field(default_factory=list)
    selected_relationship_roles: list[str] = field(default_factory=list)
    requested_relationship_roles: list[str] = field(default_factory=list)
    relationship_role_selection_mode: Optional[str] = None
    relationship_primary_role: Optional[str] = None
    relationship_topic: Optional[str] = None
    relationship_boundary_notes: list[str] = field(default_factory=list)
    cueing_style: Optional[str] = None

    # Trace accumulation, kept separated by kind
    agents: list[TraceStep] = field(default_factory=list)
    tools: list[TraceStep] = field(default_factory=list)
    guards: list[TraceStep] = field(default_factory=list)
    state_event_step: Optional[TraceStep] = None

    @property
    def has_state_event(self) -> bool:
        return self.state_event is not None
