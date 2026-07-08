from fastapi.testclient import TestClient


def _chat(client: TestClient, user_id: str, message: str) -> dict:
    response = client.post("/api/chat", json={"user_id": user_id, "message": message})
    assert response.status_code == 200
    return response.json()


def _memories(client: TestClient, user_id: str) -> list[dict]:
    response = client.get(f"/api/memory/{user_id}")
    assert response.status_code == 200
    return response.json()["memories"]


def _cards(client: TestClient, user_id: str) -> list[dict]:
    response = client.get(f"/api/memory-cards/{user_id}")
    assert response.status_code == 200
    return response.json()["cards"]


def test_chat_interest_auto_saves_without_card(client):
    uid = "triage_interest"
    body = _chat(client, uid, "我喜欢听粤剧")

    memories = _memories(client, uid)
    assert [m["content"] for m in memories] == ["喜欢听粤剧"]
    assert memories[0]["category"] == "profile_preference"
    assert _cards(client, uid) == []

    triage_steps = [
        s for s in body["agent_trace"]["tools"] if s["name"] == "MemoryTriagePolicy"
    ]
    assert triage_steps
    assert triage_steps[-1]["detail"]["decision"]["action"] == "auto_save"
    assert triage_steps[-1]["detail"]["decision"]["ask_now"] is False


def test_chat_fact_creates_pending_card_not_memory(client):
    uid = "triage_fact"
    body = _chat(client, uid, "我年轻时做过教师")

    assert _memories(client, uid) == []
    cards = _cards(client, uid)
    assert len(cards) == 1
    assert cards[0]["candidate_type"] == "fact"
    assert cards[0]["summary"] == "我年轻时做过教师"
    assert cards[0]["status"] == "pending"

    triage = [
        s for s in body["agent_trace"]["tools"] if s["name"] == "MemoryTriagePolicy"
    ][-1]
    assert triage["detail"]["decision"]["action"] == "create_card"
    assert triage["detail"]["memory_card_id"] == cards[0]["card_id"]


def test_chat_boundary_creates_boundary_card(client):
    uid = "triage_boundary"
    _chat(client, uid, "我不想再聊老伴去世的事")

    assert _memories(client, uid) == []
    cards = _cards(client, uid)
    assert len(cards) == 1
    assert cards[0]["candidate_type"] == "boundary_preference"
    assert cards[0]["summary"] == "不想再聊老伴去世的事"


def test_chat_sensitive_and_temporary_mood_do_not_write(client):
    uid = "triage_ignore"
    _chat(client, uid, "老伴去世以后我一个人住")
    _chat(client, uid, "我今天有点烦")

    assert _memories(client, uid) == []
    assert _cards(client, uid) == []


def test_chat_memory_off_blocks_extract_card_and_write(client):
    uid = "triage_memory_off"
    client.patch(f"/api/users/{uid}/profile", json={"memory_enabled": False})
    body = _chat(client, uid, "我喜欢粤剧")

    assert _memories(client, uid) == []
    assert _cards(client, uid) == []
    assert not [
        s for s in body["agent_trace"]["tools"] if s["name"] == "MemoryTriagePolicy"
    ]


def test_chat_similar_interest_does_not_duplicate(client):
    uid = "triage_duplicate"
    _chat(client, uid, "我喜欢粤剧")
    body = _chat(client, uid, "我爱听粤剧")

    memories = _memories(client, uid)
    assert [m["content"] for m in memories] == ["喜欢粤剧"]
    assert _cards(client, uid) == []

    triage = [
        s for s in body["agent_trace"]["tools"] if s["name"] == "MemoryTriagePolicy"
    ][-1]
    assert triage["detail"]["decision"]["action"] == "update_existing"
    assert triage["detail"]["decision"]["cooldown_applied"] is True
