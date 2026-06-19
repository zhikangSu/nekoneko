def test_chat_then_fetch_trace_by_turn_id(client):
    turn_id = client.post("/api/chat", json={"message": "你好"}).json()["turn_id"]

    record = client.get(f"/api/traces/{turn_id}")
    assert record.status_code == 200
    body = record.json()
    assert body["turn_id"] == turn_id
    assert body["trace"]["route"] == "companion_chat"
    assert "created_at" in body


def test_list_traces_includes_recent_turn(client):
    turn_id = client.post(
        "/api/chat", json={"user_id": "list_demo", "message": "你好"}
    ).json()["turn_id"]

    listed = client.get("/api/traces", params={"user_id": "list_demo"})
    assert listed.status_code == 200
    turn_ids = [row["turn_id"] for row in listed.json()]
    assert turn_id in turn_ids


def test_missing_trace_returns_404(client):
    assert client.get("/api/traces/t_does_not_exist").status_code == 404
