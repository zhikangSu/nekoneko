"""Sensor Simulator + proactive care endpoints (issues #22, #12).

    GET  /api/sensors/presets          list mock presets
    POST /api/sensors/apply-preset     preset → RawSignal → StateEvent → Guardian
    POST /api/sensors/refuse           user refuses a care type → cooldown pause

The flow makes the boundary explicit: SensorAdapter encodes the raw signal into
a StateEvent, and GuardianAgent decides on the StateEvent (never raw values).
The decision is persisted as a trace, so it shows in the Trace Panel.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.agents.guardian import GuardianAgent
from app.api.deps import get_guardian_store, get_profile_store, get_trace_store
from app.core.config import Settings, get_settings
from app.core.constants import CompanionMode, RiskLevel, Route, TraceEntryKind
from app.schemas.sensor import (
    ApplyPresetRequest,
    ApplyPresetResponse,
    GuardianDecisionType,
    RefuseRequest,
    SensorPreset,
    Severity,
)
from app.schemas.trace import AgentTrace, TraceRecord, TraceStep
from app.services.proactive_preferences import resolve_proactive_effective
from app.stores.guardian_state_store import GuardianStateStore
from app.stores.profile_store import ProfileStore
from app.stores.trace_store import TraceStore
from app.tools.sensor_adapter import SensorAdapter
from app.tools.sensor_simulator import SensorSimulatorTool

router = APIRouter(prefix="/sensors", tags=["sensors"])

_simulator = SensorSimulatorTool()
_adapter = SensorAdapter()

_SEVERITY_TO_RISK = {
    Severity.none: RiskLevel.low,
    Severity.low: RiskLevel.low,
    Severity.medium: RiskLevel.medium,
    Severity.high: RiskLevel.high,
}


def _risk_level(state_event, decision) -> RiskLevel:
    # A safety escalation is never "low"; otherwise follow the event severity.
    if decision.decision == GuardianDecisionType.safety_escalation:
        return RiskLevel.high
    return _SEVERITY_TO_RISK[state_event.severity]


@router.get("/presets", response_model=list[SensorPreset])
def list_presets() -> list[SensorPreset]:
    return _simulator.list_presets()


@router.post("/apply-preset", response_model=ApplyPresetResponse)
def apply_preset(
    request: ApplyPresetRequest,
    settings: Settings = Depends(get_settings),
    guardian_store: GuardianStateStore = Depends(get_guardian_store),
    profile_store: ProfileStore = Depends(get_profile_store),
    trace_store: TraceStore = Depends(get_trace_store),
) -> ApplyPresetResponse:
    preset = _simulator.get(request.preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="unknown preset")

    now = datetime.now(timezone.utc)
    profile = profile_store.get(request.user_id)
    proactive_effective = resolve_proactive_effective(profile, settings)
    state_event = _adapter.encode(preset.raw_signal, now=now)
    guardian = GuardianAgent(guardian_store, settings)
    decision = guardian.decide(
        user_id=request.user_id,
        state_event=state_event,
        now=now,
        user_proactive_enabled=profile.proactive_checkin_enabled,
        user_quiet_hours_start=profile.proactive_quiet_hours_start,
        user_quiet_hours_end=profile.proactive_quiet_hours_end,
        user_max_checkins_per_day=profile.proactive_max_checkins_per_day,
        user_same_topic_cooldown_minutes=(
            profile.proactive_same_topic_cooldown_minutes
        ),
    )

    turn_id = f"t_{uuid.uuid4().hex[:8]}"
    trace = AgentTrace(
        turn_id=turn_id,
        mode=CompanionMode.role_first,
        route=Route.proactive_checkin,
        risk_level=_risk_level(state_event, decision),
        agents=[
            TraceStep(
                kind=TraceEntryKind.agent,
                name=guardian.name,
                summary=decision.trace_visible_summary,
                detail={
                    "decision": decision.decision.value,
                    "restraint_critique": decision.restraint_critique,
                    "reason": decision.reason,
                    "cooldown_applied": decision.cooldown_applied,
                    "cooldown_minutes": decision.cooldown_minutes,
                    "profile_preferences": {
                        "proactive_checkin_enabled": (
                            profile.proactive_checkin_enabled
                        ),
                        **proactive_effective.model_dump(),
                    },
                    "profile_overrides": {
                        "quiet_hours_start": profile.proactive_quiet_hours_start,
                        "quiet_hours_end": profile.proactive_quiet_hours_end,
                        "max_checkins_per_day": profile.proactive_max_checkins_per_day,
                        "same_topic_cooldown_minutes": (
                            profile.proactive_same_topic_cooldown_minutes
                        ),
                    },
                },
            )
        ],
        tools=[
            TraceStep(
                kind=TraceEntryKind.tool,
                name=_adapter.name,
                summary=f"{preset.label}：raw → {state_event.event_type.value}",
                detail={
                    "preset_id": preset.id,
                    "raw_signal": preset.raw_signal.model_dump(),
                    "event_type": state_event.event_type.value,
                },
            )
        ],
        state_event=TraceStep(
            kind=TraceEntryKind.state_event,
            name="StateEvent",
            summary=(
                f"{state_event.event_type.value}"
                f"（severity={state_event.severity.value}, "
                f"confidence={state_event.confidence}）"
            ),
            detail={
                "event_type": state_event.event_type.value,
                "severity": state_event.severity.value,
                "confidence": state_event.confidence,
                "rationale": state_event.rationale,
                "suggested_action": state_event.suggested_action,
                "medical_claim_allowed": state_event.medical_claim_allowed,
                "source": state_event.source,
            },
        ),
    )

    trace_store.save(
        TraceRecord(
            turn_id=turn_id,
            user_id=request.user_id,
            created_at=now.isoformat(),
            trace=trace,
        )
    )

    return ApplyPresetResponse(
        turn_id=turn_id,
        raw_signal=preset.raw_signal,
        state_event=state_event,
        guardian_decision=decision,
        response_text=decision.care_proposal,
        agent_trace=trace,
    )


@router.post("/refuse", status_code=204)
def refuse_care(
    request: RefuseRequest,
    settings: Settings = Depends(get_settings),
    guardian_store: GuardianStateStore = Depends(get_guardian_store),
) -> None:
    until = datetime.now(timezone.utc) + timedelta(
        hours=settings.proactive_refusal_pause_hours
    )
    try:
        guardian_store.record_refusal(request.user_id, request.event_type.value, until)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
