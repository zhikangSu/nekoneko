from app.agents.safety_critic import SafetyCriticAgent
from app.safety.risk_keywords import RISK_CATEGORIES
from app.safety.risk_classifier import classify_risk


def test_every_category_has_a_nonempty_template():
    critic = SafetyCriticAgent()
    for category in RISK_CATEGORIES:
        cls = classify_risk(category.keywords[0])
        result = critic.review(cls)
        assert result.template == category.template
        assert result.response_text.strip()


def test_medical_symptom_does_not_diagnose():
    cls = classify_risk("我胸口痛，是不是心脏病？")
    result = SafetyCriticAgent().review(cls)
    assert "医生" in result.response_text
    # Refuses to judge the illness rather than confirming one.
    assert "没办法" in result.response_text or "不能" in result.response_text


def test_medication_refuses_dosage():
    cls = classify_risk("我忘了吃药，现在能不能吃两片？")
    result = SafetyCriticAgent().review(cls)
    assert result.template == "medication_zh.md"
    assert "按医嘱" in result.response_text


def test_fall_uses_emergency_language_and_demo_disclaimer():
    cls = classify_risk("我摔倒了，起不来。")
    result = SafetyCriticAgent().review(cls)
    assert "急救" in result.response_text
    assert "演示" in result.response_text  # makes clear no real call is placed


# --- end-to-end through /api/chat -------------------------------------------


def test_chat_medical_symptom_routes_to_safety(client):
    body = client.post(
        "/api/chat", json={"message": "我胸口痛，是不是心脏病？"}
    ).json()
    trace = body["agent_trace"]
    assert trace["route"] == "safety_response"
    assert trace["risk_level"] == "high"
    assert trace["safety_critic_used"] is True
    assert "医生" in body["response_text"]


def test_chat_medication_no_dosage_advice(client):
    body = client.post(
        "/api/chat", json={"message": "我忘了吃药，现在能不能吃两片？"}
    ).json()
    assert body["agent_trace"]["route"] == "safety_response"
    assert body["agent_trace"]["safety_critic_used"] is True
    assert "按医嘱" in body["response_text"]


def test_chat_fall_routes_to_emergency_mock(client):
    body = client.post("/api/chat", json={"message": "我摔倒了，起不来"}).json()
    assert body["agent_trace"]["route"] == "emergency_mock"
    assert body["agent_trace"]["risk_level"] == "crisis"
    assert "急救" in body["response_text"]


def test_low_risk_chat_does_not_call_safety_critic(client):
    body = client.post("/api/chat", json={"message": "你好呀"}).json()
    assert body["agent_trace"]["route"] == "companion_chat"
    assert body["agent_trace"]["safety_critic_used"] is False
