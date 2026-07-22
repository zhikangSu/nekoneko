from datetime import datetime, timedelta, timezone

from app.api.deps import get_trace_store
from app.core.constants import CompanionMode, RiskLevel, Route
from app.main import app
from app.schemas.trace import AgentTrace, TraceRecord
from app.stores.trace_store import TraceStore


def _trace_record(
    turn_id: str, user_id: str, created_at: str, route: Route
) -> TraceRecord:
    return TraceRecord(
        turn_id=turn_id,
        user_id=user_id,
        created_at=created_at,
        trace=AgentTrace(
            turn_id=turn_id,
            mode=CompanionMode.role_first,
            route=route,
            risk_level=RiskLevel.low,
        ),
    )


def test_caregiver_summary_empty(client):
    response = client.get("/api/caregiver/summary?user_id=care_empty")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "care_empty"
    assert body["active_reminders"] == 0
    assert body["confirmed_reminders_today"] == 0
    assert body["proactive_events_7d"] == 0
    assert body["safety_events_7d"] == 0
    assert "不展示完整聊天记录" in body["privacy_boundaries"]


def test_caregiver_summary_is_privacy_preserving(client):
    uid = "care_demo"
    reminder = client.post(
        f"/api/reminders/{uid}",
        json={"content": "早上八点按医嘱吃药", "time": "08:00", "recurrence": "daily"},
    ).json()
    client.post(f"/api/reminders/{uid}/{reminder['id']}/confirm")
    client.post(
        "/api/sensors/apply-preset", json={"user_id": uid, "preset_id": "poor_sleep"}
    )
    client.post("/api/chat", json={"user_id": uid, "message": "我胸口痛"})

    response = client.get(f"/api/caregiver/summary?user_id={uid}")
    assert response.status_code == 200
    body = response.json()

    assert body["active_reminders"] == 1
    assert body["confirmed_reminders_today"] == 1
    assert body["proactive_events_7d"] >= 1
    assert body["safety_events_7d"] >= 1

    reminder_digest = body["reminders"][0]
    assert reminder_digest["label"] == "提醒 1"
    assert reminder_digest["time"] == "08:00"
    assert "content" not in reminder_digest
    assert "早上八点按医嘱吃药" not in response.text
    assert "我胸口痛" not in response.text


def test_caregiver_7d_counts_not_capped_by_limit(client, tmp_path):
    uid = "care_window"
    store = TraceStore(tmp_path)
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    store.save(
        _trace_record("t_proactive", uid, yesterday.isoformat(), Route.proactive_checkin)
    )
    store.save(
        _trace_record(
            "t_safety",
            uid,
            (yesterday + timedelta(minutes=1)).isoformat(),
            Route.safety_response,
        )
    )
    store.save(
        _trace_record(
            "t_outside_window",
            uid,
            (now - timedelta(days=10)).isoformat(),
            Route.proactive_checkin,
        )
    )
    for i in range(25):
        store.save(
            _trace_record(
                f"t_chat_{i}",
                uid,
                (now - timedelta(minutes=i)).isoformat(),
                Route.companion_chat,
            )
        )

    app.dependency_overrides[get_trace_store] = lambda: store
    try:
        default_limit = client.get(f"/api/caregiver/summary?user_id={uid}")
        wide_limit = client.get(f"/api/caregiver/summary?user_id={uid}&limit=100")
    finally:
        app.dependency_overrides.clear()

    assert default_limit.status_code == 200
    body = default_limit.json()
    assert body["proactive_events_7d"] == 1
    assert body["safety_events_7d"] == 1

    wide_body = wide_limit.json()
    assert wide_body["proactive_events_7d"] == 1
    assert wide_body["safety_events_7d"] == 1
    assert [e["turn_id"] for e in wide_body["proactive_events"]] == ["t_proactive"]
    assert [e["turn_id"] for e in wide_body["safety_events"]] == ["t_safety"]
