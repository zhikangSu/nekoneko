def test_chat_returns_response_and_trace(client):
    response = client.post(
        "/api/chat",
        json={
            "user_id": "demo_user",
            "message": "我今天有点想老伴了。",
            "mode": "role_first",
        },
    )
    assert response.status_code == 200
    body = response.json()

    assert body["response_text"].strip()
    assert body["turn_id"]
    assert body["audio_url"] is None

    trace = body["agent_trace"]
    assert trace["turn_id"] == body["turn_id"]
    assert trace["mode"] == "role_first"
    assert trace["route"] == "companion_chat"
    assert trace["risk_level"] == "low"
    assert trace["retrieval_used"] is False
    assert trace["safety_critic_used"] is False
    assert trace["memory_used"] is False
    # Agent / Tool / Guard distinction is visible.
    agent_names = [s["name"] for s in trace["agents"]]
    assert "CoordinatorAgent" in agent_names
    assert "CompanionAgent" in agent_names
    assert all(s["kind"] == "agent" for s in trace["agents"])
    # Both rule guards run every turn (low-risk here, so they pass).
    guard_names = [s["name"] for s in trace["guards"]]
    assert "InputRuleGuard" in guard_names
    assert "OutputRuleGuard" in guard_names
    assert all(s["kind"] == "guard" for s in trace["guards"])
    assert trace["tools"] == []


def test_chat_defaults_mode_and_user(client):
    response = client.post("/api/chat", json={"message": "你好"})
    assert response.status_code == 200
    body = response.json()
    assert body["agent_trace"]["mode"] == "role_first"


def test_chat_neutral_assistant_mode(client):
    response = client.post(
        "/api/chat", json={"message": "帮我想想", "mode": "neutral_assistant"}
    )
    assert response.status_code == 200
    assert response.json()["agent_trace"]["mode"] == "neutral_assistant"


def test_chat_rejects_blank_message(client):
    assert client.post("/api/chat", json={"message": ""}).status_code == 422
    assert client.post("/api/chat", json={"message": "   "}).status_code == 422


def test_chat_rejects_unknown_mode(client):
    response = client.post(
        "/api/chat", json={"message": "你好", "mode": "medical_authority"}
    )
    assert response.status_code == 422


def test_turn_ids_are_unique(client):
    a = client.post("/api/chat", json={"message": "你好"}).json()["turn_id"]
    b = client.post("/api/chat", json={"message": "你好"}).json()["turn_id"]
    assert a != b


def test_fake_reply_is_safe_by_construction(client):
    # Slice 1 has no safety routing yet (#8); the baseline fake provider must
    # still never emit diagnosis or dosage content.
    response = client.post(
        "/api/chat",
        json={"message": "我忘了吃药，现在能不能吃两片？"},
    )
    assert response.status_code == 200
    text = response.json()["response_text"]
    for forbidden in ("两片", "毫克", "mg", "加倍", "多吃", "诊断"):
        assert forbidden not in text
