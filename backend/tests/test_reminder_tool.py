from datetime import date

from app.schemas.reminder import Recurrence, Reminder
from app.tools.reminder_tool import ReminderTool


def test_parse_daily_arabic():
    parsed = ReminderTool.parse("每天早上8点提醒我吃药")
    assert parsed.recurrence == Recurrence.daily
    assert parsed.time == "08:00"
    assert parsed.content == "吃药"
    assert parsed.date is None


def test_parse_daily_chinese_numeral():
    parsed = ReminderTool.parse("每天早上八点提醒我吃药")
    assert parsed.time == "08:00"
    assert parsed.content == "吃药"


def test_parse_pm_period():
    parsed = ReminderTool.parse("提醒我下午三点喝水", today=date(2026, 6, 20))
    assert parsed.time == "15:00"
    assert parsed.content == "喝水"
    assert parsed.recurrence == Recurrence.once


def test_parse_half_hour():
    parsed = ReminderTool.parse("每天晚上7点半提醒我散步")
    assert parsed.time == "19:30"
    assert parsed.content == "散步"


def test_parse_hhmm():
    parsed = ReminderTool.parse("每天8:05提醒我量血压")
    assert parsed.time == "08:05"
    assert "量血压" in parsed.content


def test_parse_tomorrow_sets_date():
    parsed = ReminderTool.parse("明天下午三点提醒我去医院", today=date(2026, 6, 20))
    assert parsed.recurrence == Recurrence.once
    assert parsed.date == "2026-06-21"
    assert parsed.time == "15:00"


def test_parse_without_time_returns_none():
    assert ReminderTool.parse("提醒我记得吃饭") is None


def test_is_reminder_request():
    assert ReminderTool.is_reminder_request("每天早上8点提醒我吃药") is True
    assert ReminderTool.is_reminder_request("今天天气不错") is False
    assert ReminderTool.is_reminder_request("提醒我一下") is False  # no time


def test_medication_confirm_says_yizhu_no_dose():
    reminder = Reminder(
        id="r_1",
        user_id="u",
        content="吃药",
        time="08:00",
        recurrence=Recurrence.daily,
        created_at="2026-06-20T00:00:00+00:00",
    )
    phrase = ReminderTool.confirm_phrase(reminder)
    assert "08:00" in phrase
    assert "按医嘱" in phrase
    for dose in ("两片", "几片", "毫克", "多吃"):
        assert dose not in phrase
