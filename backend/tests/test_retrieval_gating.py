"""Controlled retrieval gating (issue #13).

Only time-sensitive external facts (weather / air quality) retrieve. Emotional /
reminiscence turns do not; medication dosage questions route to safety and never
search for a dose.
"""


def test_weather_turn_uses_retrieval(client):
    body = client.post(
        "/api/chat", json={"message": "今天下午适合出去散步吗？"}
    ).json()
    trace = body["agent_trace"]
    assert trace["route"] == "retrieval_supported_response"
    assert trace["retrieval_used"] is True
    assert any(s["name"] == "InfoRetrievalTool" for s in trace["tools"])
    # the mock weather fact is surfaced in the reply
    assert "22" in body["response_text"] or "出门" in body["response_text"]


def test_air_quality_turn_uses_retrieval(client):
    body = client.post("/api/chat", json={"message": "今天空气质量好不好"}).json()
    assert body["agent_trace"]["route"] == "retrieval_supported_response"
    assert body["agent_trace"]["retrieval_used"] is True


def test_emotional_turn_does_not_use_retrieval(client):
    body = client.post("/api/chat", json={"message": "我今天有点孤单"}).json()
    assert body["agent_trace"]["route"] == "companion_chat"
    assert body["agent_trace"]["retrieval_used"] is False


def test_reminiscence_turn_does_not_use_retrieval(client):
    body = client.post(
        "/api/chat", json={"message": "我年轻的时候喜欢听粤剧"}
    ).json()
    assert body["agent_trace"]["retrieval_used"] is False


def test_liking_walking_does_not_use_retrieval(client):
    # 「我喜欢散步」is companionship, not a weather question.
    body = client.post("/api/chat", json={"message": "我喜欢散步"}).json()
    assert body["agent_trace"]["route"] == "companion_chat"
    assert body["agent_trace"]["retrieval_used"] is False


def test_dosage_question_routes_to_safety_not_retrieval(client):
    body = client.post(
        "/api/chat", json={"message": "我能不能补两片药？"}
    ).json()
    trace = body["agent_trace"]
    assert trace["route"] == "safety_response"
    assert trace["retrieval_used"] is False
    assert "按医嘱" in body["response_text"]
