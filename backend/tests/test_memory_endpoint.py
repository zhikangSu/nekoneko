import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_memory_store
from app.main import app
from app.stores.memory_store import MemoryStore


@pytest.fixture
def mem_client(tmp_path):
    app.dependency_overrides[get_memory_store] = lambda: MemoryStore(tmp_path)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_memory_crud(mem_client):
    empty = mem_client.get("/api/memory/demo_user").json()
    assert empty["memories"] == []
    assert empty["settings"]["extraction_paused"] is False

    created = mem_client.post(
        "/api/memory/demo_user",
        json={"category": "profile_preference", "content": "喜欢粤剧"},
    )
    assert created.status_code == 201
    memory_id = created.json()["id"]

    assert len(mem_client.get("/api/memory/demo_user").json()["memories"]) == 1

    assert mem_client.delete(f"/api/memory/demo_user/{memory_id}").status_code == 204
    assert mem_client.get("/api/memory/demo_user").json()["memories"] == []
    assert mem_client.delete("/api/memory/demo_user/missing").status_code == 404


def test_memory_pause(mem_client):
    result = mem_client.patch(
        "/api/memory/demo_user/settings", json={"extraction_paused": True}
    ).json()
    assert result["extraction_paused"] is True


# --- chat integration (uses the default store shared via conftest) ----------


def test_chat_extracts_and_reuses_preference(client):
    uid = "mem_chat_demo"
    first = client.post(
        "/api/chat", json={"user_id": uid, "message": "我喜欢听粤剧"}
    ).json()
    # A memory was extracted and written this turn.
    assert any(s["detail"].get("saved") for s in first["agent_trace"]["tools"])

    stored = client.get(f"/api/memory/{uid}").json()
    assert any("粤剧" in m["content"] for m in stored["memories"])

    # A later turn reads the memory back (memory_used flips on).
    second = client.post(
        "/api/chat", json={"user_id": uid, "message": "今天有点无聊"}
    ).json()
    assert second["agent_trace"]["memory_used"] is True


def test_paused_chat_does_not_extract(client):
    uid = "mem_paused_demo"
    client.patch(f"/api/memory/{uid}/settings", json={"extraction_paused": True})
    body = client.post(
        "/api/chat", json={"user_id": uid, "message": "我喜欢喝茶"}
    ).json()
    assert not any(s["detail"].get("saved") for s in body["agent_trace"]["tools"])
    assert client.get(f"/api/memory/{uid}").json()["memories"] == []


def test_chat_respects_profile_memory_disabled(client):
    # The profile master switch (memory_enabled=false) skips both read and write.
    uid = "mem_disabled_demo"
    client.patch(
        f"/api/users/{uid}/profile",
        json={"memory_enabled": False, "onboarding_completed": True},
    )
    body = client.post(
        "/api/chat", json={"user_id": uid, "message": "我喜欢听评书"}
    ).json()
    trace = body["agent_trace"]
    assert trace["memory_used"] is False
    # nothing written
    assert not any(s["detail"].get("saved") for s in trace["tools"])
    assert client.get(f"/api/memory/{uid}").json()["memories"] == []
    # the trace explains memory was off
    mem_steps = [s for s in trace["tools"] if s["name"] == "MemoryTool"]
    assert any(s["detail"].get("memory_enabled") is False for s in mem_steps)


def test_blank_memory_content_rejected(mem_client):
    response = mem_client.post(
        "/api/memory/demo_user",
        json={"category": "event_memory", "content": "   "},
    )
    assert response.status_code == 422


def test_reminder_category_cannot_be_added_to_long_term_memory(mem_client):
    response = mem_client.post(
        "/api/memory/demo_user",
        json={"category": "reminder_or_setting", "content": "每天八点吃药"},
    )
    assert response.status_code == 422
