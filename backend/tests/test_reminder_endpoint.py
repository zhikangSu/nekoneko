import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_reminder_store
from app.main import app
from app.stores.reminder_store import ReminderStore


@pytest.fixture
def rem_client(tmp_path):
    app.dependency_overrides[get_reminder_store] = lambda: ReminderStore(tmp_path)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_reminder_crud_confirm_trigger(rem_client):
    created = rem_client.post(
        "/api/reminders/demo_user",
        json={"content": "吃药", "time": "08:00", "recurrence": "daily"},
    )
    assert created.status_code == 201
    reminder_id = created.json()["id"]

    assert len(rem_client.get("/api/reminders/demo_user").json()) == 1

    confirmed = rem_client.post(
        f"/api/reminders/demo_user/{reminder_id}/confirm"
    ).json()
    assert confirmed["last_confirmed_at"] is not None

    fired = rem_client.post(
        f"/api/reminders/demo_user/{reminder_id}/trigger"
    ).json()
    assert "吃药" in fired["message"]
    assert "按医嘱" in fired["message"]

    assert rem_client.delete(f"/api/reminders/demo_user/{reminder_id}").status_code == 204
    assert rem_client.get("/api/reminders/demo_user").json() == []


def test_invalid_time_rejected(rem_client):
    response = rem_client.post(
        "/api/reminders/demo_user", json={"content": "x", "time": "25:00"}
    )
    assert response.status_code == 422


def test_one_off_reminder_requires_valid_date(rem_client):
    missing = rem_client.post(
        "/api/reminders/demo_user",
        json={"content": "复诊", "time": "09:30", "recurrence": "once"},
    )
    assert missing.status_code == 422

    invalid = rem_client.post(
        "/api/reminders/demo_user",
        json={
            "content": "复诊",
            "time": "09:30",
            "recurrence": "once",
            "date": "2026-02-30",
        },
    )
    assert invalid.status_code == 422

    created = rem_client.post(
        "/api/reminders/demo_user",
        json={
            "content": "复诊",
            "time": "09:30",
            "recurrence": "once",
            "date": "2026-07-25",
        },
    )
    assert created.status_code == 201
    assert created.json()["date"] == "2026-07-25"


def test_daily_reminder_rejects_irrelevant_date(rem_client):
    response = rem_client.post(
        "/api/reminders/demo_user",
        json={
            "content": "喝水",
            "time": "10:00",
            "recurrence": "daily",
            "date": "2026-07-25",
        },
    )
    assert response.status_code == 422


def test_trigger_missing_returns_404(rem_client):
    assert rem_client.post("/api/reminders/demo_user/missing/trigger").status_code == 404


def test_blank_content_rejected(rem_client):
    response = rem_client.post(
        "/api/reminders/demo_user", json={"content": "   ", "time": "08:00"}
    )
    assert response.status_code == 422


# --- chat integration (default store shared via conftest) -------------------


def test_chat_creates_medication_reminder(client):
    uid = "rem_chat_demo"
    body = client.post(
        "/api/chat", json={"user_id": uid, "message": "每天早上8点提醒我吃药"}
    ).json()
    assert body["agent_trace"]["route"] == "reminder_management"
    assert "按医嘱" in body["response_text"]
    assert "08:00" in body["response_text"]

    reminders = client.get(f"/api/reminders/{uid}").json()
    assert any(r["content"] == "吃药" and r["time"] == "08:00" for r in reminders)
    assert client.get(f"/api/memory/{uid}").json()["memories"] == []


def test_chat_dosage_question_routes_to_safety(client):
    body = client.post(
        "/api/chat", json={"message": "我能不能多吃一片药？"}
    ).json()
    assert body["agent_trace"]["route"] == "safety_response"
    assert body["agent_trace"]["safety_critic_used"] is True
