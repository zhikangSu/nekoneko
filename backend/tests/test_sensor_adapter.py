from datetime import datetime, timezone

from app.schemas.sensor import StateEventType
from app.tools.sensor_adapter import SensorAdapter
from app.tools.sensor_simulator import SensorSimulatorTool

_NOW = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)


def _encode(preset_id: str):
    preset = SensorSimulatorTool().get(preset_id)
    return SensorAdapter().encode(preset.raw_signal, now=_NOW)


def test_preset_to_event_mapping():
    assert _encode("normal_day").event_type == StateEventType.NORMAL_DAY
    assert _encode("poor_sleep").event_type == StateEventType.POOR_SLEEP
    assert _encode("low_activity").event_type == StateEventType.LOW_ACTIVITY
    assert _encode("medication_missed").event_type == StateEventType.REMINDER_OVERDUE
    assert _encode("no_response").event_type == StateEventType.LONG_NO_RESPONSE
    assert _encode("low_mood").event_type == StateEventType.LOW_MOOD_SELF_REPORT
    assert (
        _encode("elevated_hr_mock").event_type
        == StateEventType.PHYSIOLOGICAL_ANOMALY_MOCK
    )


def test_hr_anomaly_is_low_confidence_and_no_medical_claim():
    event = _encode("elevated_hr_mock")
    assert event.confidence <= 0.4
    assert event.medical_claim_allowed is False


def test_no_event_allows_medical_claim():
    for preset_id in (
        "normal_day",
        "poor_sleep",
        "low_activity",
        "medication_missed",
        "no_response",
        "low_mood",
        "elevated_hr_mock",
    ):
        assert _encode(preset_id).medical_claim_allowed is False


def test_event_carries_confidence_and_rationale():
    event = _encode("low_activity")
    assert 0.0 <= event.confidence <= 1.0
    assert event.rationale
