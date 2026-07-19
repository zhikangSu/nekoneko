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
    # Memory read runs on the companion path (kind=memory, in the tools list).
    assert any(s["name"] == "MemoryTool" for s in trace["tools"])


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


def test_manual_role_selection_guides_companion_chat_trace(client):
    response = client.post(
        "/api/chat",
        json={
            "user_id": "manual_elder_role_chat",
            "message": "我终于也是活到了我妈妈的那个年纪",
            "role_selection_mode": "manual",
            "selected_role_ids": ["elder_mentor"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["agent_trace"]["route"] == "companion_chat"
    assert body["role_messages"] == []

    role_trace = body["agent_trace"]["research_trace"]["role"]
    assert role_trace["role_selection_mode"] == "manual"
    assert role_trace["requested_role_ids"] == ["elder_mentor"]
    assert role_trace["selected_roles"] == ["elder_mentor"]
    assert role_trace["primary_role"] == "elder_mentor"

    companion_step = next(
        step
        for step in body["agent_trace"]["agents"]
        if step["name"] == "CompanionAgent"
    )
    assert companion_step["detail"]["manual_role_style"] is True
    assert companion_step["detail"]["role_labels"] == ["长辈引导者"]
    assert "长辈引导者" in companion_step["summary"]
    assert "陪伴 AI" not in companion_step["summary"]


def test_auto_role_selection_trace_respects_loneliness_cue_exclusion(client):
    response = client.post(
        "/api/chat",
        json={
            "user_id": "auto_role_chat",
            "message": "我今天一个人在家，心情有点复杂，想找人聊聊",
            "role_selection_mode": "auto",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["agent_trace"]["route"] == "companion_chat"
    assert body["role_messages"] == []

    role_trace = body["agent_trace"]["research_trace"]["role"]
    assert role_trace["role_selection_mode"] == "auto"
    assert role_trace["requested_role_ids"] == []
    assert role_trace["selected_roles"]
    assert "no_ai_role" not in role_trace["selected_roles"]

    orchestrator_step = next(
        step
        for step in body["agent_trace"]["agents"]
        if step["name"] == "RelationshipOrchestratorAgent"
    )
    assert orchestrator_step["detail"]["auto_role_style"] is True

    companion_step = next(
        step
        for step in body["agent_trace"]["agents"]
        if step["name"] == "CompanionAgent"
    )
    assert companion_step["detail"]["auto_role_style"] is False
    assert companion_step["detail"]["selected_roles"] == []
    assert companion_step["detail"]["role_labels"] == []
    assert "系统分配关系角色" not in companion_step["summary"]


def test_manual_no_ai_role_does_not_auto_allocate_companion_chat(client):
    response = client.post(
        "/api/chat",
        json={
            "user_id": "manual_no_ai_role_chat",
            "message": "我就想自己说说",
            "role_selection_mode": "manual",
            "selected_role_ids": ["no_ai_role"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    role_trace = body["agent_trace"]["research_trace"]["role"]
    assert role_trace["role_selection_mode"] == "manual"
    assert role_trace["requested_role_ids"] == ["no_ai_role"]
    assert role_trace["selected_roles"] == ["no_ai_role"]
    assert role_trace["primary_role"] == "no_ai_role"
    companion_step = next(
        step
        for step in body["agent_trace"]["agents"]
        if step["name"] == "CompanionAgent"
    )
    assert "百事通" in companion_step["summary"]
    assert "陪伴 AI" not in companion_step["summary"]
    assert "RelationshipOrchestratorAgent" not in [
        step["name"] for step in body["agent_trace"]["agents"]
    ]


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
