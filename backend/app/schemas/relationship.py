"""Relationship role schemas for the reminiscence companion (issue #51).

These describe *relationship functions* the companion can lean into when helping
an older adult reminisce — a same-age peer who shares the era, a curious junior
who asks one gentle question, a boundary guardian who steps in on sensitive
topics, and so on. They are **not** autonomous agents: only CoordinatorAgent,
CompanionAgent, GuardianAgent, and SafetyCriticAgent appear as autonomous agents
in code and trace (CLAUDE.md §8). A visible relationship role is a stance the
CompanionAgent adopts, never a separate LLM agent.

Hard product boundary (AGENTS.md, CLAUDE.md §7): a relationship role never
impersonates a real family member, a real acquaintance, or the deceased. It
offers a familiar *function* (era resonance, curiosity, mentoring, boundary
care), not a fake identity.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RoleId(str, Enum):
    """Stable identifiers for the eight visible relationship roles (Study 1 R1–R8)."""

    same_age_peer = "same_age_peer"  # R1
    curious_junior = "curious_junior"  # R2
    middle_age_bridge = "middle_age_bridge"  # R3
    elder_mentor = "elder_mentor"  # R4
    theme_companion = "theme_companion"  # R5
    memory_organizer = "memory_organizer"  # R6
    boundary_guardian = "boundary_guardian"  # R7
    no_ai_role = "no_ai_role"  # R8


class RoleProfile(BaseModel):
    """A visible relationship function the companion can adopt for one turn.

    A profile is descriptive data, not a runnable agent: ``is_autonomous_agent``
    is always ``False``. ``is_visible_to_user`` is ``True`` because these roles
    are meant to be surfaced to the older adult (and family), unlike the internal
    autonomous agents.
    """

    role_id: RoleId
    label_zh: str
    label_en: str
    relationship_function: str
    best_for_topics: list[str]
    not_for_topics: list[str] = Field(default_factory=list)
    speaking_style: str
    example_opening: str
    boundary_rules: list[str]
    is_visible_to_user: bool = True
    is_autonomous_agent: bool = False
