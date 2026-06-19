"""UserProfile models (issue #21).

The profile owns identity/onboarding state, including the user-chosen
``companion_display_name``. It is the source of truth the CompanionAgent (#6)
reads from. A name is never hardcoded; when unset the UI/prompt fall back to the
neutral label (AGENTS.md §4.1, §10).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

_NAME_MAX = 40


class UserProfile(BaseModel):
    user_id: str
    companion_display_name: Optional[str] = None
    user_display_name: Optional[str] = None
    onboarding_completed: bool = False
    memory_enabled: bool = True
    proactive_checkin_enabled: bool = True


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


def normalize_name(value: Optional[str]) -> Optional[str]:
    """Trim a display name; blank becomes ``None`` (cleared)."""
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None
