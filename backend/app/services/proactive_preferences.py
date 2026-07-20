"""Resolve Guardian preferences without confusing defaults with overrides."""

from __future__ import annotations

from app.core.config import Settings
from app.schemas.profile import ProactiveEffective, UserProfile


def resolve_proactive_effective(
    profile: UserProfile,
    settings: Settings,
) -> ProactiveEffective:
    """Resolve profile override → Settings/env (which owns built-in defaults)."""

    return ProactiveEffective(
        quiet_hours_start=(
            profile.proactive_quiet_hours_start
            if profile.proactive_quiet_hours_start is not None
            else settings.quiet_hours_start
        ),
        quiet_hours_end=(
            profile.proactive_quiet_hours_end
            if profile.proactive_quiet_hours_end is not None
            else settings.quiet_hours_end
        ),
        max_checkins_per_day=(
            profile.proactive_max_checkins_per_day
            if profile.proactive_max_checkins_per_day is not None
            else settings.proactive_max_checkins_per_day
        ),
        same_topic_cooldown_minutes=(
            profile.proactive_same_topic_cooldown_minutes
            if profile.proactive_same_topic_cooldown_minutes is not None
            else settings.proactive_same_topic_cooldown_minutes
        ),
    )
