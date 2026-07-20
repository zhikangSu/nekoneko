"""Reminder models (issue #11).

Medication reminders only ever say "按医嘱" — never a dose or quantity. Dosage
questions route to safety (#8), not here.
"""

from __future__ import annotations

import re
from datetime import date as calendar_date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Recurrence(str, Enum):
    once = "once"
    daily = "daily"


class Reminder(BaseModel):
    id: str
    user_id: str
    content: str
    time: str  # HH:MM (24h)
    recurrence: Recurrence
    date: Optional[str] = None  # YYYY-MM-DD, for one-off reminders
    created_at: str
    active: bool = True
    last_confirmed_at: Optional[str] = None


class ReminderCreate(BaseModel):
    content: str = Field(min_length=1, max_length=200)
    time: str
    recurrence: Recurrence = Recurrence.daily
    date: Optional[str] = None

    @field_validator("content")
    @classmethod
    def _content_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("content must not be blank")
        return stripped

    @field_validator("time")
    @classmethod
    def _valid_time(cls, value: str) -> str:
        if not _TIME_RE.match(value):
            raise ValueError("time must be HH:MM (24h)")
        return value

    @field_validator("date")
    @classmethod
    def _valid_date(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            if not _DATE_RE.match(value):
                raise ValueError("date must be YYYY-MM-DD")
            try:
                calendar_date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("date must be a valid calendar date") from exc
        return value

    @model_validator(mode="after")
    def _date_matches_recurrence(self) -> "ReminderCreate":
        if self.recurrence == Recurrence.once and self.date is None:
            raise ValueError("date is required for one-off reminders")
        if self.recurrence == Recurrence.daily and self.date is not None:
            raise ValueError("date is only allowed for one-off reminders")
        return self
