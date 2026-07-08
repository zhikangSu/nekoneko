"""``POST /api/chat`` — runs the agent graph and persists the trace.

    input guard → coordinator → (companion | safety | proactive) → output guard

The trace records the Agent / Tool / Guard steps for this turn and is saved so
the Trace history API (#9) can return it by ``turn_id``.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from app.api.deps import get_profile_store, get_trace_store
from app.core.config import Settings, get_settings
from app.graph.build_graph import build_deps, run_turn
from app.graph.state import GraphState
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.relationship import ElderControlAction
from app.schemas.trace import AgentTrace, ResearchTraceMetadata, TraceRecord
from app.stores.profile_store import ProfileStore
from app.stores.trace_store import TraceStore

router = APIRouter(tags=["chat"])


def _new_turn_id() -> str:
    return f"t_{uuid.uuid4().hex[:8]}"


def _research_metadata(state: GraphState) -> dict:
    metadata: dict = {
        "study_condition": state.study_condition.value,
        "elder_control_action": state.elder_control_action.value,
    }
    if state.study_session_id:
        metadata["study_session_id"] = state.study_session_id
    if state.topic_id:
        metadata["topic_id"] = state.topic_id
    if state.topic_label:
        metadata["topic_label"] = state.topic_label
    if state.material_type:
        metadata["material_type"] = state.material_type.value
    if state.selected_relationship_roles:
        metadata["selected_roles"] = state.selected_relationship_roles
    if state.cueing_style:
        metadata["cueing_style"] = state.cueing_style
    return metadata


def _boundary_state(state: GraphState) -> str:
    if state.elder_control_action == ElderControlAction.pause_roles:
        return "user_paused_roles"
    if state.elder_control_action == ElderControlAction.stop_reminiscence:
        return "user_stopped_reminiscence"
    if state.relationship_boundary_notes:
        return "guarded"
    return "none"


def _research_trace(state: GraphState) -> ResearchTraceMetadata:
    return ResearchTraceMetadata.model_validate(
        {
            "role": {
                "selected_roles": state.selected_relationship_roles,
                "primary_role": state.relationship_primary_role,
                "role_selection_mode": (
                    state.relationship_role_selection_mode
                    or state.role_selection_mode.value
                ),
                "requested_role_ids": state.requested_relationship_roles,
                "cueing_style": state.cueing_style,
            },
            "topic": {
                "topic_id": state.topic_id,
                "topic_label": state.topic_label,
                "material_type": (
                    state.material_type.value if state.material_type else None
                ),
                "classified_topic": state.relationship_topic,
            },
            "boundary": {
                "boundary_state": _boundary_state(state),
                "boundary_notes": state.relationship_boundary_notes,
            },
            "control": {
                "study_condition": state.study_condition.value,
                "study_session_id": state.study_session_id,
                "elder_control_action": state.elder_control_action.value,
            },
        }
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
    profile_store: ProfileStore = Depends(get_profile_store),
    trace_store: TraceStore = Depends(get_trace_store),
) -> ChatResponse:
    # Companion name source of truth is the user profile (#21).
    profile = profile_store.get(request.user_id)
    turn_id = _new_turn_id()

    state = GraphState(
        turn_id=turn_id,
        user_id=request.user_id,
        user_input=request.message,
        mode=request.mode,
        user_profile=profile,
        role_selection_mode=request.role_selection_mode,
        selected_role_ids=request.selected_role_ids,
        topic_id=request.topic_id,
        topic_label=request.topic_label,
        material_type=request.material_type,
        study_condition=request.study_condition,
        study_session_id=request.study_session_id,
        elder_control_action=request.elder_control_action,
    )
    run_turn(state, build_deps(settings))

    trace = AgentTrace(
        turn_id=turn_id,
        mode=request.mode,
        route=state.route,
        risk_level=state.risk.level,
        agents=state.agents,
        tools=state.tools,
        guards=state.guards,
        state_event=state.state_event_step,
        memory_used=state.memory_used,
        retrieval_used=state.retrieval_used,
        safety_critic_used=state.safety_critic_used,
        research_metadata=_research_metadata(state),
        research_trace=_research_trace(state),
    )

    trace_store.save(
        TraceRecord(
            turn_id=turn_id,
            user_id=request.user_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            trace=trace,
        )
    )

    return ChatResponse(
        turn_id=turn_id,
        response_text=state.response_text,
        role_messages=state.role_messages,
        audio_url=None,
        agent_trace=trace,
    )
