"""``POST /api/chat`` — text-chat loop.

The reply is produced by ``CompanionAgent`` (#6), which reads the user's
``companion_display_name`` from the profile (#21) into the mode prompt. Routing
(CoordinatorAgent #5) and guards/safety (#8) plug in here later; for now every
turn is a low-risk companion chat.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.agents.companion import CompanionAgent
from app.api.deps import get_profile_store
from app.core.config import Settings, get_settings
from app.core.constants import RiskLevel, Route, TraceEntryKind
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.trace import AgentTrace, TraceStep
from app.services.llm_provider import get_llm_provider
from app.stores.profile_store import ProfileStore

router = APIRouter(tags=["chat"])


def _new_turn_id() -> str:
    return f"t_{uuid.uuid4().hex[:8]}"


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
    profile_store: ProfileStore = Depends(get_profile_store),
) -> ChatResponse:
    # Source of truth for the companion name is the user profile (#21).
    profile = profile_store.get(request.user_id)

    agent = CompanionAgent(get_llm_provider(settings))
    result = agent.respond(
        message=request.message,
        mode=request.mode,
        companion_display_name=profile.companion_display_name,
    )

    turn_id = _new_turn_id()
    trace = AgentTrace(
        turn_id=turn_id,
        mode=request.mode,
        route=Route.companion_chat,
        risk_level=RiskLevel.low,
        agents=[
            TraceStep(
                kind=TraceEntryKind.agent,
                name=agent.name,
                summary=result.trace_summary(),
                detail={
                    "mode": result.mode.value,
                    "companion_display_name": result.companion_display_name,
                    "named_by_user": result.named_by_user,
                    "prompt_version": agent.prompt_version,
                    "prompt_preview": result.rendered_prompt[:140],
                },
            )
        ],
        memory_used=False,
        retrieval_used=False,
        safety_critic_used=False,
    )

    return ChatResponse(
        turn_id=turn_id,
        response_text=result.reply_text,
        audio_url=None,
        agent_trace=trace,
    )
