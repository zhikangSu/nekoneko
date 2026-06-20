"""GuardianAgent — restrained proactive care (issue #12).

Consumes a structured ``StateEvent`` (never raw sensor values), combines it with
cross-turn ``welfare_state``, and decides care-vs-restraint: check_in / defer /
silent_log / safety_escalation. It never diagnoses and never makes a medical
claim from a sensor preset (AGENTS.md §11). Restraint: same-type cooldown, a
daily cap, quiet hours, and a refusal pause.
"""

from __future__ import annotations

from datetime import datetime, time, timedelta

from app.core.config import Settings
from app.schemas.sensor import (
    GuardianDecision,
    GuardianDecisionType,
    StateEvent,
    StateEventType,
)
from app.stores.guardian_state_store import GuardianStateStore

_ESCALATION_EVENTS = {StateEventType.LONG_NO_RESPONSE}
_SILENT_EVENTS = {StateEventType.NORMAL_DAY, StateEventType.PHYSIOLOGICAL_ANOMALY_MOCK}

_CARE_MESSAGES: dict[StateEventType, str] = {
    StateEventType.POOR_SLEEP: "看起来昨晚可能没睡太好。如果现在方便，我可以陪您聊两句。",
    StateEventType.LOW_ACTIVITY: "今天好像还没怎么走动。要不要待会儿一起活动一下，或者先陪您说说话？",
    StateEventType.REMINDER_OVERDUE: "到吃药的时间了。具体怎么吃请按医嘱，我只帮您记得这个时间点。",
    StateEventType.LOW_MOOD_SELF_REPORT: "我在的。如果您愿意，我可以陪您说一会儿，您想聊聊吗？",
    StateEventType.LONG_NO_RESPONSE: (
        "好一会儿没有您的消息了，我有点惦记您。您还好吗？如果不太方便，"
        "也可以联系一下家人或邻居；要是紧急情况，请联系当地急救。"
    ),
}


def _parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def _in_quiet_hours(now: datetime, start: time, end: time) -> bool:
    current = now.time()
    if start <= end:
        return start <= current < end
    return current >= start or current < end  # window crosses midnight


class GuardianAgent:
    name = "GuardianAgent"

    def __init__(self, store: GuardianStateStore, settings: Settings):
        self._store = store
        self._settings = settings

    def decide(
        self,
        *,
        user_id: str,
        state_event: StateEvent,
        now: datetime,
        user_proactive_enabled: bool = True,
    ) -> GuardianDecision:
        event = state_event.event_type
        name = event.value
        cooldown_minutes = self._settings.proactive_same_topic_cooldown_minutes

        if not self._settings.proactive_enabled:
            return self._silent(name, "主动关怀已全局关闭")

        if event in _SILENT_EVENTS:
            reason = (
                "各项信号正常，无需打扰"
                if event == StateEventType.NORMAL_DAY
                else "低置信度的模拟生理信号，不做任何医学解释，仅记录、不主动打扰"
            )
            return self._silent(name, reason)

        is_escalation = event in _ESCALATION_EVENTS

        # User preference and refusal suppress only casual check-ins — a
        # safety_escalation (e.g. long no-response) is never silenced by them.
        if not is_escalation and not user_proactive_enabled:
            return self._silent(name, "用户已在设置中关闭主动关怀问候")

        if not is_escalation and self._store.is_refused(user_id, name, now):
            return self._defer(name, "用户近期拒绝了同类关怀，正处于暂停期内")

        if not is_escalation and _in_quiet_hours(
            now,
            _parse_hhmm(self._settings.quiet_hours_start),
            _parse_hhmm(self._settings.quiet_hours_end),
        ):
            return self._defer(name, "处于安静时段（默认 22:00–07:00），非紧急不打扰")

        last = self._store.last_checkin_at(user_id, name)
        if (
            not is_escalation
            and last is not None
            and (now - last) < timedelta(minutes=cooldown_minutes)
        ):
            return self._defer(name, f"同类关怀冷却中（{cooldown_minutes} 分钟内已问候过）")

        if (
            not is_escalation
            and self._store.checkins_today(user_id, now)
            >= self._settings.proactive_max_checkins_per_day
        ):
            cap = self._settings.proactive_max_checkins_per_day
            return self._silent(name, f"今日主动关怀已达上限（{cap} 次），改为静默记录")

        # Surface the care.
        self._store.record_checkin(user_id, name, now)
        decision = (
            GuardianDecisionType.safety_escalation
            if is_escalation
            else GuardianDecisionType.check_in
        )
        critique = "综合安静时段、冷却与每日上限后，认为现在适合温和开口。"
        if is_escalation:
            critique += "（长时间无响应属于关怀升级，不受安静时段限制，但仍只建议联系家人/急救，不替代真实救援。）"
        return GuardianDecision(
            decision=decision,
            care_proposal=_CARE_MESSAGES[event],
            restraint_critique=critique,
            reason=state_event.rationale,
            cooldown_applied=True,
            cooldown_minutes=cooldown_minutes,
            trace_visible_summary=f"{name} → {decision.value}",
        )

    # --- helpers ------------------------------------------------------------

    def _silent(self, name: str, reason: str) -> GuardianDecision:
        return GuardianDecision(
            decision=GuardianDecisionType.silent_log,
            care_proposal="",
            restraint_critique="本次不主动开口。",
            reason=reason,
            cooldown_applied=False,
            cooldown_minutes=0,
            trace_visible_summary=f"{name} → silent_log（{reason}）",
        )

    def _defer(self, name: str, reason: str) -> GuardianDecision:
        return GuardianDecision(
            decision=GuardianDecisionType.defer,
            care_proposal="",
            restraint_critique=reason,
            reason=reason,
            cooldown_applied=False,
            cooldown_minutes=0,
            trace_visible_summary=f"{name} → defer（{reason}）",
        )
