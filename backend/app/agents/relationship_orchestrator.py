"""RelationshipOrchestratorAgent — schedules VISIBLE relationship roles (issue #52).

This is a deterministic, rule-based policy that, for a reminiscence turn,
classifies the topic and then picks which visible relationship personas (the
#51 roles: same-age peer, curious junior, boundary guardian, …) should speak,
which one leads, how they are cued in, and emits an explainable
role/topic/memory/boundary trace.

Important boundaries (CLAUDE.md §8):

* The visible relationship personas it schedules are NOT autonomous agents. Only
  CoordinatorAgent, CompanionAgent, GuardianAgent, and SafetyCriticAgent are
  autonomous agents in code and trace. This orchestrator merely *schedules
  personas* the CompanionAgent adopts.
* It is a deterministic policy the Coordinator could call — it uses rules and
  templates, never a real LLM.
* It is a new, isolated module: it does NOT modify or read the existing
  graph / safety / Guardian / Reminder / Retrieval paths.
"""

from __future__ import annotations

from app.relationship.orchestration_policy import decide
from app.relationship.role_profiles import list_role_profiles
from app.relationship.topic_classifier import classify_topic
from app.schemas.relationship import (
    OrchestrationInput,
    RelationshipDecision,
    RoleProfile,
)


class RelationshipOrchestratorAgent:
    """Rule-based scheduler of visible relationship personas for reminiscence.

    Not an autonomous agent in the CLAUDE.md §8 sense; it is a deterministic
    policy. ``name`` mirrors the other agent classes for trace consistency, but
    the personas it schedules stay visible, non-autonomous roles.
    """

    name = "RelationshipOrchestratorAgent"

    def __init__(self, roles: list[RoleProfile] | None = None) -> None:
        # Default to the full visible-role registry from #51.
        self._roles: list[RoleProfile] = roles if roles is not None else list_role_profiles()

    @property
    def roles(self) -> list[RoleProfile]:
        return list(self._roles)

    def orchestrate(self, inp: OrchestrationInput) -> RelationshipDecision:
        """Classify the topic, then apply the deterministic scheduling policy."""

        topic = classify_topic(inp.user_input)
        return decide(inp, topic, self._roles)
