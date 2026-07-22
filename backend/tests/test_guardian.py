from datetime import datetime, timedelta, timezone

from app.agents.guardian import GuardianAgent
from app.core.config import Settings
from app.schemas.sensor import (
    GuardianDecisionType,
    Severity,
    StateEvent,
    StateEventType,
)
from app.stores.guardian_state_store import GuardianStateStore

_NOON = datetime(2026, 6, 20, 10, 0, tzinfo=timezone.utc)
_NIGHT = datetime(2026, 6, 20, 23, 0, tzinfo=timezone.utc)  # quiet hours


def _event(event_type: StateEventType, severity: Severity = Severity.low) -> StateEvent:
    return StateEvent(
        event_type=event_type,
        severity=severity,
        confidence=0.7,
        rationale="r",
        suggested_action="a",
        timestamp=_NOON.isoformat(),
    )


def _guardian(tmp_path) -> GuardianAgent:
    return GuardianAgent(GuardianStateStore(tmp_path), Settings())


def test_poor_sleep_checks_in(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u", state_event=_event(StateEventType.POOR_SLEEP), now=_NOON
    )
    assert decision.decision == GuardianDecisionType.check_in
    assert decision.care_proposal


def test_anomaly_is_silent_with_no_medical_claim(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u",
        state_event=_event(StateEventType.PHYSIOLOGICAL_ANOMALY_MOCK),
        now=_NOON,
    )
    assert decision.decision == GuardianDecisionType.silent_log
    assert decision.care_proposal == ""


def test_no_response_escalates(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u",
        state_event=_event(StateEventType.LONG_NO_RESPONSE, Severity.medium),
        now=_NOON,
    )
    assert decision.decision == GuardianDecisionType.safety_escalation
    assert "家人" in decision.care_proposal or "急救" in decision.care_proposal


def test_same_type_cooldown_defers(tmp_path):
    guardian = _guardian(tmp_path)
    guardian.decide(
        user_id="u", state_event=_event(StateEventType.POOR_SLEEP), now=_NOON
    )
    second = guardian.decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON + timedelta(minutes=30),
    )
    assert second.decision == GuardianDecisionType.defer


def test_quiet_hours_defers_non_urgent(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u", state_event=_event(StateEventType.POOR_SLEEP), now=_NIGHT
    )
    assert decision.decision == GuardianDecisionType.defer


def test_user_quiet_hours_override_defers_non_urgent(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON,
        user_quiet_hours_start="09:00",
        user_quiet_hours_end="11:00",
    )
    assert decision.decision == GuardianDecisionType.defer


def test_escalation_ignores_quiet_hours(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u",
        state_event=_event(StateEventType.LONG_NO_RESPONSE, Severity.medium),
        now=_NIGHT,
    )
    assert decision.decision == GuardianDecisionType.safety_escalation


def test_daily_cap_silences(tmp_path):
    guardian = _guardian(tmp_path)
    for event_type in (
        StateEventType.POOR_SLEEP,
        StateEventType.LOW_ACTIVITY,
        StateEventType.LOW_MOOD_SELF_REPORT,
    ):
        guardian.decide(user_id="u", state_event=_event(event_type), now=_NOON)
    fourth = guardian.decide(
        user_id="u", state_event=_event(StateEventType.REMINDER_OVERDUE), now=_NOON
    )
    assert fourth.decision == GuardianDecisionType.silent_log


def test_user_daily_cap_override_silences(tmp_path):
    guardian = _guardian(tmp_path)
    first = guardian.decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON,
        user_max_checkins_per_day=1,
    )
    second = guardian.decide(
        user_id="u",
        state_event=_event(StateEventType.LOW_ACTIVITY),
        now=_NOON + timedelta(minutes=1),
        user_max_checkins_per_day=1,
    )
    assert first.decision == GuardianDecisionType.check_in
    assert second.decision == GuardianDecisionType.silent_log


def test_env_quiet_hours_apply_when_profile_override_unset(tmp_path, monkeypatch):
    monkeypatch.setenv("QUIET_HOURS_START", "09:00")
    monkeypatch.setenv("QUIET_HOURS_END", "11:00")
    decision = GuardianAgent(GuardianStateStore(tmp_path), Settings()).decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON,
    )
    assert decision.decision == GuardianDecisionType.defer


def test_profile_override_beats_env_quiet_hours(tmp_path, monkeypatch):
    monkeypatch.setenv("QUIET_HOURS_START", "09:00")
    monkeypatch.setenv("QUIET_HOURS_END", "11:00")
    decision = GuardianAgent(GuardianStateStore(tmp_path), Settings()).decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON,
        user_quiet_hours_start="14:00",
        user_quiet_hours_end="15:00",
    )
    assert decision.decision == GuardianDecisionType.check_in


def test_env_quiet_hours_do_not_silence_escalation(tmp_path, monkeypatch):
    monkeypatch.setenv("QUIET_HOURS_START", "09:00")
    monkeypatch.setenv("QUIET_HOURS_END", "11:00")
    decision = GuardianAgent(GuardianStateStore(tmp_path), Settings()).decide(
        user_id="u",
        state_event=_event(StateEventType.LONG_NO_RESPONSE, Severity.medium),
        now=_NOON,
    )
    assert decision.decision == GuardianDecisionType.safety_escalation


def test_user_cooldown_override_allows_sooner_checkin(tmp_path):
    guardian = _guardian(tmp_path)
    guardian.decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON,
        user_same_topic_cooldown_minutes=30,
    )
    second = guardian.decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON + timedelta(minutes=45),
        user_same_topic_cooldown_minutes=30,
    )
    assert second.decision == GuardianDecisionType.check_in


def test_refusal_pauses_same_type(tmp_path):
    store = GuardianStateStore(tmp_path)
    store.record_refusal("u", "POOR_SLEEP", _NOON + timedelta(hours=10))
    decision = GuardianAgent(store, Settings()).decide(
        user_id="u", state_event=_event(StateEventType.POOR_SLEEP), now=_NOON
    )
    assert decision.decision == GuardianDecisionType.defer


def test_user_disabled_suppresses_checkin(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u",
        state_event=_event(StateEventType.POOR_SLEEP),
        now=_NOON,
        user_proactive_enabled=False,
    )
    assert decision.decision == GuardianDecisionType.silent_log


def test_user_disabled_does_not_suppress_escalation(tmp_path):
    decision = _guardian(tmp_path).decide(
        user_id="u",
        state_event=_event(StateEventType.LONG_NO_RESPONSE, Severity.medium),
        now=_NOON,
        user_proactive_enabled=False,
    )
    assert decision.decision == GuardianDecisionType.safety_escalation


def test_refusal_does_not_suppress_escalation(tmp_path):
    store = GuardianStateStore(tmp_path)
    store.record_refusal("u", "LONG_NO_RESPONSE", _NOON + timedelta(hours=10))
    decision = GuardianAgent(store, Settings()).decide(
        user_id="u",
        state_event=_event(StateEventType.LONG_NO_RESPONSE, Severity.medium),
        now=_NOON,
    )
    assert decision.decision == GuardianDecisionType.safety_escalation
