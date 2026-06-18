"""``POST /api/chat`` — the Slice 1 minimal text-chat loop.

Returns ``response_text`` plus a baseline ``agent_trace``. Routing
(CoordinatorAgent #5), guards/safety (#8), and a real CompanionAgent (#6) plug
in here later; for now every turn is a low-risk companion chat answered by the
configured LLM provider (fake in demo mode).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.constants import (
    DEFAULT_COMPANION_DISPLAY_NAME,
    RiskLevel,
    Route,
    TraceEntryKind,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.trace import AgentTrace, TraceStep
from app.services.llm_provider import CompanionReplyInput, get_llm_provider

router = APIRouter(tags=["chat"])


def _new_turn_id() -> str:
    return f"t_{uuid.uuid4().hex[:8]}"


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    provider = get_llm_provider(settings)
    companion_name = (
        request.companion_display_name or ""
    ).strip() or DEFAULT_COMPANION_DISPLAY_NAME

    reply = provider.generate_companion_reply(
        CompanionReplyInput(
            message=request.message,
            mode=request.mode,
            companion_display_name=companion_name,
        )
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
                name="CompanionAgent",
                summary=(
                    f"Baseline companion reply via the {provider.name} LLM "
                    "provider (no routing or guards yet — Slice 1)."
                ),
                detail={"mode": request.mode.value},
            )
        ],
        memory_used=False,
        retrieval_used=False,
        safety_critic_used=False,
    )

    return ChatResponse(
        turn_id=turn_id,
        response_text=reply,
        audio_url=None,
        agent_trace=trace,
    )
