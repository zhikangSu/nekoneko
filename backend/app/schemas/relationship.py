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


class RoleSelectionMode(str, Enum):
    """Who chooses visible relationship roles for a cueing turn."""

    auto = "auto"
    manual = "manual"


class MaterialType(str, Enum):
    """Topic/material anchors used by the reminiscence prototype."""

    topic_card = "topic_card"
    photo = "photo"
    object = "object"
    song = "song"


class StudyCondition(str, Enum):
    """Study 2 comparison conditions for the relationship-aware prototype."""

    c1_direct_question = "c1_direct_question"
    c2_fixed_role_prelude = "c2_fixed_role_prelude"
    c3_relationship_aware = "c3_relationship_aware"


class ElderControlAction(str, Enum):
    """Elder-facing controls for a reminiscence session."""

    continue_session = "continue_session"
    change_topic = "change_topic"
    pause_roles = "pause_roles"
    stop_reminiscence = "stop_reminiscence"


class RoleCueMessage(BaseModel):
    """One visible role bubble rendered inside a single companion turn."""

    role_id: RoleId | None = None
    role_label: str
    text: str


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


# ---------------------------------------------------------------------------
# Orchestration schemas (issue #52)
#
# The RelationshipOrchestratorAgent is a deterministic, rule-based POLICY that
# schedules which VISIBLE relationship roles (personas above) speak on a
# reminiscence turn. Scheduling personas is not the same as spawning agents:
# these roles are still NOT autonomous agents (only CoordinatorAgent,
# CompanionAgent, GuardianAgent, and SafetyCriticAgent are — CLAUDE.md §8). The
# orchestrator emits an explainable role/topic/memory/boundary trace so the
# Coordinator (and family) can see *why* a role set was chosen.
# ---------------------------------------------------------------------------


class CueingStyle(str, Enum):
    """How the chosen roles are staged into the turn.

    * ``direct`` — a single role picks up the thread directly, no prelude.
    * ``single_role_prelude`` — one gentle role opens, then invites the elder.
    * ``agent_agent_then_invite`` — two visible personas briefly resonate with
      each other, then turn to invite the elder in. Never used on sensitive
      topics (it can feel performative around grief/health/conflict).
    * ``no_cue`` — no staged persona banter at all (sensitive topics, or the
      user wants the named CompanionAgent without research-role labels).
    """

    direct = "direct"
    single_role_prelude = "single_role_prelude"
    agent_agent_then_invite = "agent_agent_then_invite"
    no_cue = "no_cue"


class InteractionIntent(str, Enum):
    """What the current utterance is doing, separate from its content topic."""

    presence_activity = "presence_activity"
    presence_identity = "presence_identity"
    presence_hearing = "presence_hearing"
    topic_turn = "topic_turn"
    general_turn = "general_turn"


class RoleSelectionSource(str, Enum):
    """Why the current visible relationship-role set was selected."""

    policy = "policy"
    user_manual = "user_manual"
    visible_context = "visible_context"
    user_preference = "user_preference"


class OrchestrationInput(BaseModel):
    """Everything the deterministic policy needs to schedule roles for a turn."""

    user_input: str
    memory_context: list[str] = Field(default_factory=list)
    recent_emotion_or_tone: str | None = None
    user_role_preferences: dict | None = None
    role_selection_mode: RoleSelectionMode = RoleSelectionMode.auto
    selected_role_ids: list[RoleId] = Field(default_factory=list)
    # Roles already visible in the current UI scene. They preserve conversational
    # continuity but are not treated as a manual user choice.
    context_role_ids: list[RoleId] = Field(default_factory=list, max_length=3)
    risk_flags: dict | None = None


class RelationshipDecision(BaseModel):
    """Explainable result of scheduling visible relationship roles for one turn.

    Carries both the machine-actionable choice (``selected_roles`` /
    ``primary_role`` / ``cueing_style``) and four human-readable trace strings
    (role / topic / memory / boundary) plus a short visible summary, so the
    reasoning is auditable without a real LLM in the loop.
    """

    topic: str
    interaction_intent: InteractionIntent
    # Roles considered by policy before choosing the smallest useful speaker
    # set. ``selected_roles`` are the roles that actually speak this turn;
    # ``silent_roles`` remain visible/auditable but do not produce a bubble.
    candidate_roles: list[RoleId] = Field(default_factory=list)
    selected_roles: list[RoleId]
    silent_roles: list[RoleId] = Field(default_factory=list)
    primary_role: RoleId | None
    role_selection_source: RoleSelectionSource = RoleSelectionSource.policy
    cueing_style: CueingStyle
    role_selection_reason: str
    boundary_notes: list[str] = Field(default_factory=list)
    allow_follow_up: bool = False
    follow_up_reason: str = "本轮不需要追问。"
    should_generate_memory_card: bool = False
    trace_visible_summary: str
    role_trace: str
    topic_trace: str
    memory_trace: str
    boundary_trace: str
