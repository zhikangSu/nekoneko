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
