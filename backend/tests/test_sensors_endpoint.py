from datetime import datetime as _datetime, timezone

import pytest

from app.core.config import Settings, get_settings
from app.main import app


@pytest.fixture
def env_quiet_settings():
    app.dependency_overrides[get_settings] = lambda: Settings(
        quiet_hours_start="11:00",
        quiet_hours_end="13:00",
    )
    yield
    app.dependency_overrides.pop(get_settings, None)


@pytest.fixture(autouse=True)
def _fixed_daytime(monkeypatch):
    """Pin the route clock to a fixed daytime so Guardian check-in assertions are
    not flaky: quiet hours (22:00–07:00, evaluated in UTC) would otherwise flip a
    ``check_in`` to ``defer`` when the suite runs during that UTC window.
    """
    import app.api.routes.sensors as sensors_mod

    class _FixedDateTime(_datetime):
        @classmethod
        def now(cls, tz=None):
            return _datetime(2026, 6, 21, 12, 0, tzinfo=tz or timezone.utc)

    monkeypatch.setattr(sensors_mod, "datetime", _FixedDateTime)


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


def test_guardian_converts_utc_instant_to_configured_local_timezone(
    client, monkeypatch
):
    """02:30 UTC is daytime in Hong Kong and must not hit quiet hours."""

    import app.api.routes.sensors as sensors_mod

    fixed_utc = _datetime(2026, 7, 20, 2, 30, tzinfo=timezone.utc)

    class _FixedUtcInstant(_datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_utc if tz is None else fixed_utc.astimezone(tz)

    monkeypatch.setattr(sensors_mod, "datetime", _FixedUtcInstant)
    app.dependency_overrides[get_settings] = lambda: Settings(
        app_timezone="Asia/Hong_Kong"
    )
    try:
        body = client.post(
            "/api/sensors/apply-preset",
            json={"user_id": "sensor_local_daytime", "preset_id": "poor_sleep"},
        ).json()
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert body["guardian_decision"]["decision"] == "check_in"
    detail = body["agent_trace"]["agents"][0]["detail"]
    assert detail["local_timezone"] == "Asia/Hong_Kong"
    assert detail["local_time"].endswith("+08:00")


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
    # An escalation must not show risk_level "low".
    assert body["agent_trace"]["risk_level"] == "high"


def test_poor_sleep_trace_risk_is_low(client):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "sensor_risk_low", "preset_id": "poor_sleep"},
    ).json()
    assert body["agent_trace"]["risk_level"] == "low"


def test_profile_disabled_silences_checkin(client):
    uid = "sensor_proactive_off"
    client.patch(
        f"/api/users/{uid}/profile",
        json={"proactive_checkin_enabled": False, "onboarding_completed": True},
    )
    body = client.post(
        "/api/sensors/apply-preset", json={"user_id": uid, "preset_id": "poor_sleep"}
    ).json()
    assert body["guardian_decision"]["decision"] == "silent_log"


def test_profile_proactive_preferences_feed_guardian_trace(client):
    uid = "sensor_custom_proactive"
    client.patch(
        f"/api/users/{uid}/profile",
        json={
            "proactive_quiet_hours_start": "11:00",
            "proactive_quiet_hours_end": "13:00",
            "proactive_max_checkins_per_day": 1,
            "proactive_same_topic_cooldown_minutes": 45,
        },
    )
    body = client.post(
        "/api/sensors/apply-preset", json={"user_id": uid, "preset_id": "poor_sleep"}
    ).json()
    assert body["guardian_decision"]["decision"] == "defer"
    detail = body["agent_trace"]["agents"][0]["detail"]["profile_preferences"]
    assert detail["quiet_hours_start"] == "11:00"
    assert detail["quiet_hours_end"] == "13:00"
    assert detail["max_checkins_per_day"] == 1
    assert detail["same_topic_cooldown_minutes"] == 45


def test_env_guardian_config_applies_when_profile_unset(
    client,
    env_quiet_settings,
):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "sensor_env_quiet", "preset_id": "poor_sleep"},
    ).json()

    assert body["guardian_decision"]["decision"] == "defer"
    detail = body["agent_trace"]["agents"][0]["detail"]
    assert detail["profile_preferences"]["quiet_hours_start"] == "11:00"
    assert detail["profile_overrides"]["quiet_hours_start"] is None


def test_profile_override_beats_env_guardian_config(
    client,
    env_quiet_settings,
):
    uid = "sensor_env_override"
    client.patch(
        f"/api/users/{uid}/profile",
        json={
            "proactive_quiet_hours_start": "14:00",
            "proactive_quiet_hours_end": "15:00",
        },
    )
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": uid, "preset_id": "poor_sleep"},
    ).json()

    assert body["guardian_decision"]["decision"] == "check_in"


def test_patch_null_resets_profile_to_env_guardian_config(
    client,
    env_quiet_settings,
):
    uid = "sensor_env_reset"
    client.patch(
        f"/api/users/{uid}/profile",
        json={
            "proactive_quiet_hours_start": "14:00",
            "proactive_quiet_hours_end": "15:00",
        },
    )
    client.patch(
        f"/api/users/{uid}/profile",
        json={
            "proactive_quiet_hours_start": None,
            "proactive_quiet_hours_end": None,
        },
    )
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": uid, "preset_id": "poor_sleep"},
    ).json()

    assert body["guardian_decision"]["decision"] == "defer"


def test_env_quiet_hours_do_not_silence_escalation(
    client,
    env_quiet_settings,
):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "sensor_env_escalation", "preset_id": "no_response"},
    ).json()

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
