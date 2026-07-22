"""Mock caregiver dashboard endpoint (issue #79).

This route summarizes reminder completion, proactive care, and safety metadata
without returning full chat transcripts, memory contents, or real notifications.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_reminder_store, get_trace_store
from app.core.constants import RiskLevel, Route
from app.schemas.caregiver import (
    CaregiverEventDigest,
    CaregiverReminderDigest,
    CaregiverSummary,
)
from app.schemas.trace import TraceSummary
from app.stores.reminder_store import ReminderStore
from app.stores.trace_store import TraceStore

router = APIRouter(prefix="/caregiver", tags=["caregiver"])

_ROUTE_LABELS: dict[Route, str] = {
    Route.proactive_checkin: "主动关怀事件",
    Route.safety_response: "安全回复事件",
    Route.emergency_mock: "模拟紧急边界事件",
    Route.reminder_management: "提醒管理事件",
    Route.memory_management: "记忆管理事件",
    Route.retrieval_supported_response: "受控查询事件",
    Route.relationship_cueing: "关系话题引导事件",
    Route.companion_chat: "普通陪伴对话",
}

_PRIVACY_BOUNDARIES = [
    "不展示完整聊天记录",
    "不展示记忆原文或私密资料",
    "不发送真实通知或紧急呼叫",
]


def _parse_dt(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _is_today(value: str | None, now: datetime) -> bool:
    if value is None:
        return False
    parsed = _parse_dt(value)
    return parsed is not None and parsed.date() == now.date()


def _is_recent(summary: TraceSummary, cutoff: datetime) -> bool:
    parsed = _parse_dt(summary.created_at)
    return parsed is not None and parsed >= cutoff


def _is_safety_event(summary: TraceSummary) -> bool:
    return summary.route in {Route.safety_response, Route.emergency_mock} or (
        summary.risk_level in {RiskLevel.high, RiskLevel.crisis}
    )


def _event_digest(summary: TraceSummary) -> CaregiverEventDigest:
    return CaregiverEventDigest(
        turn_id=summary.turn_id,
        created_at=summary.created_at,
        route=summary.route,
        risk_level=summary.risk_level,
        summary=_ROUTE_LABELS.get(summary.route, summary.route.value),
    )


@router.get("/summary", response_model=CaregiverSummary)
def caregiver_summary(
    user_id: str = Query(default="demo_user", min_length=1, max_length=64),
    limit: int = Query(default=20, ge=1, le=100),
    reminder_store: ReminderStore = Depends(get_reminder_store),
    trace_store: TraceStore = Depends(get_trace_store),
) -> CaregiverSummary:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)
    reminders = [r for r in reminder_store.list(user_id) if r.active]
    window_traces = [
        t for t in trace_store.list(user_id=user_id, limit=None) if _is_recent(t, cutoff)
    ]
    proactive = [t for t in window_traces if t.route == Route.proactive_checkin]
    safety = [t for t in window_traces if _is_safety_event(t)]
    recent_traces = window_traces[:limit]
    recent_proactive = [t for t in recent_traces if t.route == Route.proactive_checkin]
    recent_safety = [t for t in recent_traces if _is_safety_event(t)]
    confirmed_today = sum(1 for r in reminders if _is_today(r.last_confirmed_at, now))

    return CaregiverSummary(
        user_id=user_id,
        generated_at=now.isoformat(),
        active_reminders=len(reminders),
        confirmed_reminders_today=confirmed_today,
        pending_reminders=max(0, len(reminders) - confirmed_today),
        proactive_events_7d=len(proactive),
        safety_events_7d=len(safety),
        reminders=[
            CaregiverReminderDigest(
                reminder_id=reminder.id,
                label=f"提醒 {index}",
                time=reminder.time,
                recurrence=reminder.recurrence,
                status=(
                    "confirmed_today"
                    if _is_today(reminder.last_confirmed_at, now)
                    else "pending"
                ),
                last_confirmed_at=reminder.last_confirmed_at,
            )
            for index, reminder in enumerate(reminders, start=1)
        ],
        proactive_events=[_event_digest(t) for t in recent_proactive[:5]],
        safety_events=[_event_digest(t) for t in recent_safety[:5]],
        privacy_boundaries=_PRIVACY_BOUNDARIES,
    )
