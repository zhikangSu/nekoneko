"""SensorAdapter / StateEncoder — RawSignal → StateEvent (issue #22).

Deterministic rules turn a mock signal into a structured ``StateEvent`` that the
GuardianAgent consumes. The adapter never makes a medical claim: every event has
``medical_claim_allowed=False``, and the mock physiological anomaly is low
confidence by construction. GuardianAgent must read the StateEvent, not the raw
values.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from app.schemas.sensor import RawSignal, Severity, StateEvent, StateEventType

_NO_RESPONSE_HOURS = 8.0
_MEDICATION_OVERDUE_MIN = 60
_HR_DELTA_THRESHOLD = 25
_POOR_SLEEP_HOURS = 5.0
_LOW_ACTIVITY_STEPS = 100


class SensorAdapter:
    name = "SensorAdapter"

    def encode(self, signal: RawSignal, *, now: Optional[datetime] = None) -> StateEvent:
        timestamp = (now or datetime.now(timezone.utc)).isoformat()

        # Ordered most-concerning first; the first matching rule wins.
        if signal.last_interaction_hours >= _NO_RESPONSE_HOURS:
            return StateEvent(
                event_type=StateEventType.LONG_NO_RESPONSE,
                severity=Severity.medium,
                confidence=0.7,
                rationale=f"已经约 {signal.last_interaction_hours:.0f} 小时没有互动，比平时久一些。",
                suggested_action="可以温和确认是否一切都好，并提示可联系家人或邻居。",
                timestamp=timestamp,
            )

        if signal.medication_overdue_minutes >= _MEDICATION_OVERDUE_MIN:
            return StateEvent(
                event_type=StateEventType.REMINDER_OVERDUE,
                severity=Severity.low,
                confidence=0.9,
                rationale=f"用药时间已过约 {signal.medication_overdue_minutes} 分钟。",
                suggested_action="可以温和提醒，但只说按医嘱，不判断剂量。",
                timestamp=timestamp,
            )

        if (signal.self_reported_mood or "").lower() == "low":
            return StateEvent(
                event_type=StateEventType.LOW_MOOD_SELF_REPORT,
                severity=Severity.medium,
                confidence=0.85,
                rationale="用户自述心情低落。",
                suggested_action="先情绪承接，温和陪伴，必要时提示联系信任的人。",
                timestamp=timestamp,
            )

        if signal.heart_rate_current - signal.heart_rate_baseline >= _HR_DELTA_THRESHOLD:
            return StateEvent(
                event_type=StateEventType.PHYSIOLOGICAL_ANOMALY_MOCK,
                severity=Severity.low,
                confidence=0.3,  # low by construction — a mock signal proves nothing
                rationale=(
                    f"心率（{signal.heart_rate_current}）高于基线"
                    f"（{signal.heart_rate_baseline}），但这是模拟信号，无法据此判断健康状况。"
                ),
                suggested_action="不要做任何医学解释；仅可在不提健康结论的前提下温和关心。",
                medical_claim_allowed=False,
                timestamp=timestamp,
            )

        if signal.sleep_duration_hours < _POOR_SLEEP_HOURS:
            return StateEvent(
                event_type=StateEventType.POOR_SLEEP,
                severity=Severity.low,
                confidence=0.7,
                rationale=f"睡眠约 {signal.sleep_duration_hours:.1f} 小时，比平时少一点。",
                suggested_action="可以用不确定的措辞温和问候，不要断定身体不好。",
                timestamp=timestamp,
            )

        if signal.steps_last_3h < _LOW_ACTIVITY_STEPS:
            return StateEvent(
                event_type=StateEventType.LOW_ACTIVITY,
                severity=Severity.low,
                confidence=0.6,
                rationale=f"近三小时步数约 {signal.steps_last_3h}，活动比平时少。",
                suggested_action="可以轻轻问候，不要断定原因。",
                timestamp=timestamp,
            )

        return StateEvent(
            event_type=StateEventType.NORMAL_DAY,
            severity=Severity.none,
            confidence=0.9,
            rationale="各项信号都在平时范围内。",
            suggested_action="无需主动打扰，记录即可。",
            timestamp=timestamp,
        )
