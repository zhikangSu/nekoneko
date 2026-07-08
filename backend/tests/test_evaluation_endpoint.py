def test_evaluation_export_empty(client):
    response = client.get("/api/evaluation/export", params={"user_id": "eval_empty"})
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "eval_empty"
    assert body["trace_count"] == 0
    assert body["route_counts"] == {}
    assert body["risk_counts"] == {}
    assert body["rows"] == []


def test_evaluation_export_summarizes_trace_metadata_without_transcript(client):
    uid = "eval_demo"
    client.post("/api/chat", json={"user_id": uid, "message": "你好，今天想聊聊天"})
    client.post("/api/chat", json={"user_id": uid, "message": "我胸口痛"})

    response = client.get("/api/evaluation/export", params={"user_id": uid})
    assert response.status_code == 200
    body = response.json()

    assert body["trace_count"] >= 2
    assert body["route_counts"]["companion_chat"] >= 1
    assert body["route_counts"]["safety_response"] >= 1
    assert body["risk_counts"]["low"] >= 1
    assert "你好，今天想聊聊天" not in response.text
    assert "我胸口痛" not in response.text


def test_evaluation_csv_export_contains_only_summary_columns(client):
    uid = "eval_csv"
    client.post("/api/chat", json={"user_id": uid, "message": "你好"})

    response = client.get("/api/evaluation/export.csv", params={"user_id": uid})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    text = response.text
    assert "turn_id,created_at,route,risk_level,safety_critic_used,retrieval_used" in text
    assert "companion_chat" in text
    assert "你好" not in text
