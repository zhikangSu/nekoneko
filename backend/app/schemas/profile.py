"""UserProfile models (issue #21).

The profile owns identity/onboarding state, including the user-chosen
``companion_display_name``. It is the source of truth the CompanionAgent (#6)
reads from. A name is never hardcoded; when unset the UI/prompt fall back to the
neutral label (AGENTS.md §4.1, §10).
"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

_NAME_MAX = 40
_HHMM = re.compile(r"^\d{2}:\d{2}$")


def _validate_hhmm(value: str) -> str:
    if not _HHMM.match(value):
        raise ValueError("time must use HH:MM format")
    hour, minute = (int(part) for part in value.split(":"))
    if hour > 23 or minute > 59:
        raise ValueError("time must be a valid 24-hour clock value")
    return value


class UserProfile(BaseModel):
    user_id: str
    companion_display_name: Optional[str] = None
    user_display_name: Optional[str] = None
    onboarding_completed: bool = False
    memory_enabled: bool = True
    proactive_checkin_enabled: bool = True
    proactive_quiet_hours_start: str = "22:00"
    proactive_quiet_hours_end: str = "07:00"
    proactive_max_checkins_per_day: int = Field(default=3, ge=0, le=6)
    proactive_same_topic_cooldown_minutes: int = Field(default=120, ge=0, le=720)

    @field_validator("proactive_quiet_hours_start", "proactive_quiet_hours_end")
    @classmethod
    def validate_quiet_hours(cls, value: str) -> str:
        return _validate_hhmm(value)


class ProfileUpdate(BaseModel):
    """Partial update. Only fields explicitly sent are changed.

    To clear a name, send an empty string (or null); it normalizes to ``None``
    so the neutral fallback applies again.
    """

    companion_display_name: Optional[str] = Field(default=None, max_length=_NAME_MAX)
    user_display_name: Optional[str] = Field(default=None, max_length=_NAME_MAX)
    onboarding_completed: Optional[bool] = None
    memory_enabled: Optional[bool] = None
    proactive_checkin_enabled: Optional[bool] = None
    proactive_quiet_hours_start: Optional[str] = None
    proactive_quiet_hours_end: Optional[str] = None
    proactive_max_checkins_per_day: Optional[int] = Field(default=None, ge=0, le=6)
    proactive_same_topic_cooldown_minutes: Optional[int] = Field(
        default=None, ge=0, le=720
    )

    @field_validator("proactive_quiet_hours_start", "proactive_quiet_hours_end")
    @classmethod
    def validate_quiet_hours(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return _validate_hhmm(value)


def normalize_name(value: Optional[str]) -> Optional[str]:
    """Trim a display name; blank becomes ``None`` (cleared)."""
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None
