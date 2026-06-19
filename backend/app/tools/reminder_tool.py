"""ReminderTool — parse/create reminders + restate confirmation (issue #11).

Deterministic Chinese time parsing for demo mode (no LLM): turns
「每天早上8点提醒我吃药」into a daily 08:00 "吃药" reminder. Medication reminders
only ever say "按医嘱" — never a dose. Dosage questions are routed to safety
(#8), not here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

from app.schemas.reminder import Recurrence
from app.stores.reminder_store import ReminderStore

_CN = {
    "零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
}

_HHMM_RE = re.compile(r"(\d{1,2})[:：](\d{2})")
_CN_TIME_RE = re.compile(
    r"(早上|上午|清晨|中午|下午|晚上|傍晚|夜里)?\s*"
    r"(\d{1,2}|[零一二两三四五六七八九十]+)\s*点"
    r"(?:\s*(半|[0-5]?\d|[零一二三四五六七八九十]+)\s*分?)?"
)
_PM_PERIODS = {"下午", "晚上", "傍晚", "夜里"}
_TRIGGER_WORDS = ("提醒", "别忘", "记得", "叫我")
_STRIP_WORDS = (
    "每天", "每日", "明天", "今天", "提醒我", "提醒", "叫我", "记得", "别忘了",
    "别忘", "一下", "帮我", "请", "早上", "上午", "清晨", "中午", "下午",
    "晚上", "傍晚", "夜里",
)


def _cn_to_int(token: str) -> Optional[int]:
    token = token.strip()
    if not token:
        return None
    if token.isdigit():
        return int(token)
    if token == "十":
        return 10
    if "十" in token:
        left, _, right = token.partition("十")
        tens = _CN.get(left, 1) if left else 1
        ones = _CN.get(right, 0) if right else 0
        return tens * 10 + ones
    return _CN.get(token)


@dataclass
class ParsedReminder:
    content: str
    time: str
    recurrence: Recurrence
    date: Optional[str]


def _parse_time(text: str) -> Optional[tuple[str, tuple[int, int]]]:
    match = _HHMM_RE.search(text)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}", match.span()

    match = _CN_TIME_RE.search(text)
    if not match:
        return None
    period, hour_token, minute_token = match.group(1), match.group(2), match.group(3)
    hour = _cn_to_int(hour_token)
    if hour is None:
        return None
    minute = 0
    if minute_token:
        minute = 30 if minute_token == "半" else (_cn_to_int(minute_token) or 0)
    if period in _PM_PERIODS and hour < 12:
        hour += 12
    elif period == "中午" and hour < 12:
        hour = 12
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return f"{hour:02d}:{minute:02d}", match.span()


def _extract_content(text: str, time_span: tuple[int, int]) -> str:
    stripped = text[: time_span[0]] + text[time_span[1] :]
    for word in _STRIP_WORDS:
        stripped = stripped.replace(word, "")
    return stripped.strip(" 。，、!！?？.…:：\t")


def _parse_recurrence(text: str, today: date) -> tuple[Recurrence, Optional[str]]:
    if "每天" in text or "每日" in text:
        return Recurrence.daily, None
    if "明天" in text:
        return Recurrence.once, (today + timedelta(days=1)).isoformat()
    return Recurrence.once, today.isoformat()


class ReminderTool:
    name = "ReminderTool"

    def __init__(self, store: ReminderStore):
        self._store = store

    @staticmethod
    def is_reminder_request(text: str) -> bool:
        text = text or ""
        return any(w in text for w in _TRIGGER_WORDS) and _parse_time(text) is not None

    @staticmethod
    def parse(text: str, today: Optional[date] = None) -> Optional[ParsedReminder]:
        today = today or date.today()
        parsed_time = _parse_time(text or "")
        if parsed_time is None:
            return None
        time_str, span = parsed_time
        content = _extract_content(text, span) or "提醒"
        recurrence, when = _parse_recurrence(text, today)
        return ParsedReminder(content=content, time=time_str, recurrence=recurrence, date=when)

    def create_from_text(self, user_id: str, text: str):
        parsed = self.parse(text)
        if parsed is None:
            return None
        return self._store.add(
            user_id,
            content=parsed.content,
            time=parsed.time,
            recurrence=parsed.recurrence,
            date=parsed.date,
        )

    @staticmethod
    def fire_message(reminder) -> str:
        """The spoken text when a reminder is triggered (demo only)."""
        message = f"到时间啦，记得{reminder.content}。"
        if "药" in reminder.content:
            message += "用药请按医嘱。"
        return message

    @staticmethod
    def confirm_phrase(reminder) -> str:
        when = "每天" if reminder.recurrence == Recurrence.daily else (reminder.date or "")
        phrase = f"好的，我帮您记下了：{when} {reminder.time} 提醒您{reminder.content}。".replace(
            "  ", " "
        )
        if "药" in reminder.content:
            phrase += "用药请按医嘱，我只负责按时提醒，不判断该吃多少。"
        return phrase
