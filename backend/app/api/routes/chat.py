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
from app.schemas.trace import AgentTrace, TraceRecord
from app.stores.profile_store import ProfileStore
from app.stores.trace_store import TraceStore

router = APIRouter(tags=["chat"])


def _new_turn_id() -> str:
    return f"t_{uuid.uuid4().hex[:8]}"


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
        audio_url=None,
        agent_trace=trace,
    )
