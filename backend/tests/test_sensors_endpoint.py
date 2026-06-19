def test_list_presets(client):
    response = client.get("/api/sensors/presets")
    assert response.status_code == 200
    ids = [p["id"] for p in response.json()]
    assert "poor_sleep" in ids
    assert "elevated_hr_mock" in ids
    assert "no_response" in ids


def test_apply_poor_sleep_checks_in_and_persists_trace(client):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "sensor_u1", "preset_id": "poor_sleep"},
    ).json()
    assert body["state_event"]["event_type"] == "POOR_SLEEP"
    assert body["guardian_decision"]["decision"] == "check_in"
    assert body["response_text"]
    # the trace shows SensorAdapter (tool) + GuardianAgent (agent) + StateEvent
    trace = body["agent_trace"]
    assert any(s["name"] == "SensorAdapter" for s in trace["tools"])
    assert any(s["name"] == "GuardianAgent" for s in trace["agents"])
    assert trace["state_event"]["kind"] == "state_event"
    # persisted and fetchable
    assert client.get(f"/api/traces/{body['turn_id']}").status_code == 200


def test_apply_elevated_hr_makes_no_medical_claim(client):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "sensor_u2", "preset_id": "elevated_hr_mock"},
    ).json()
    event = body["state_event"]
    assert event["event_type"] == "PHYSIOLOGICAL_ANOMALY_MOCK"
    assert event["medical_claim_allowed"] is False
    assert event["confidence"] <= 0.4
    assert body["guardian_decision"]["decision"] == "silent_log"
    assert body["response_text"] == ""


def test_apply_no_response_escalates(client):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "sensor_u3", "preset_id": "no_response"},
    ).json()
    assert body["state_event"]["event_type"] == "LONG_NO_RESPONSE"
    assert body["guardian_decision"]["decision"] == "safety_escalation"


def test_refuse_then_defer(client):
    uid = "sensor_refuse"
    first = client.post(
        "/api/sensors/apply-preset", json={"user_id": uid, "preset_id": "poor_sleep"}
    ).json()
    assert first["guardian_decision"]["decision"] == "check_in"

    assert (
        client.post(
            "/api/sensors/refuse",
            json={"user_id": uid, "event_type": "POOR_SLEEP"},
        ).status_code
        == 204
    )

    second = client.post(
        "/api/sensors/apply-preset", json={"user_id": uid, "preset_id": "poor_sleep"}
    ).json()
    assert second["guardian_decision"]["decision"] == "defer"


def test_unknown_preset_404(client):
    assert (
        client.post(
            "/api/sensors/apply-preset", json={"preset_id": "nope"}
        ).status_code
        == 404
    )
