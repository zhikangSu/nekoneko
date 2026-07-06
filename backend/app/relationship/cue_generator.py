"""Rule-based relationship-cue generator (issue #53).

Turns a :class:`RelationshipDecision` (from the deterministic
RelationshipOrchestratorAgent, #52) into a short, visible social cue for a
NON-SENSITIVE reminiscence turn: two or three VISIBLE relationship roles briefly
resonate about the shared object/topic, then the last line gently invites the
elder in — without forcing an answer.

This is pure templates — NO LLM. It stages VISIBLE relationship personas (from
#51); those personas are not autonomous agents. It never touches the existing
safety / Guardian / Reminder / Retrieval paths.

Hard product boundaries (AGENTS.md, CLAUDE.md §7, §8):

* A role NEVER impersonates a real family member, a real acquaintance, or the
  deceased. It offers a familiar *function* (era resonance, curiosity,
  mentoring), not a fake identity.
* NEVER use dependency / stickiness language (「只有我懂您」/「别结束再聊一会儿」).
* At most ``MAX_ROLES_PER_TURN`` role lines, one short sentence per role, each
  line prefixed with the role's ``label_zh`` + "：".
"""

from __future__ import annotations

from app.relationship.role_profiles import MAX_ROLES_PER_TURN, get_role_profile
from app.relationship.topic_classifier import Topic, classify_topic
from app.schemas.relationship import (
    CueingStyle,
    RelationshipDecision,
    RoleId,
)


# The NON-SENSITIVE reminiscence topics that route to relationship_cueing.
# Explicitly EXCLUDES SENSITIVE_TOPICS (deceased_grief / health_care /
# privacy_family_conflict), loneliness_mood, and other — those stay on the
# existing companion path so grief/loneliness are never staged into persona
# banter (CLAUDE.md §7.3, non-regression guard).
CUE_ROUTE_TOPICS: frozenset[Topic] = frozenset(
    {
        Topic.old_object_photo,
        Topic.work_collective,
        Topic.family_education,
        Topic.culture_arts,
        Topic.general_reminiscence,
    }
)


def is_relationship_cue_turn(text: str) -> bool:
    """True only for NON-SENSITIVE reminiscence turns that should be cued.

    Sensitive topics, loneliness, and everything else stay on the companion
    path, so existing routing/tests are preserved.
    """

    return classify_topic(text) in CUE_ROUTE_TOPICS


# ---------------------------------------------------------------------------
# Per-role resonance / invitation templates.
#
# Each role has (a) a short "resonate" line — it reacts to the shared
# object/topic — and (b) a short "invite" line that gently turns to the elder
# without forcing an answer. Templates may vary by topic; a per-role default
# covers topics without a specific template. Every line is ONE short sentence.
# ---------------------------------------------------------------------------

# _RESONATE[role][topic] -> line; _RESONATE[role][None] -> default.
_RESONATE: dict[RoleId, dict[Topic | None, str]] = {
    RoleId.same_age_peer: {
        Topic.old_object_photo: "这样的老物件我们那会儿家家都有，一看见就想起从前的日子。",
        Topic.work_collective: "那会儿在单位、在大院里一块儿忙活的日子，想起来真亲切。",
        Topic.culture_arts: "这些老段子、老曲子我们那代人都听着长大，一听就有味道。",
        Topic.family_education: "那时候拉扯孩子不容易，我们那代人都是这么一步步过来的。",
        Topic.general_reminiscence: "您说的这些，我们那会儿也常经历，一提起来就觉得亲切。",
        None: "您说的这些，我们那会儿也常经历，一提起来就觉得亲切。",
    },
    RoleId.curious_junior: {
        Topic.old_object_photo: "这台老电视当年是不是很稀罕呀，您还记得头一回打开它是什么时候吗？",
        Topic.work_collective: "那时候在单位是做什么活儿的呀，听起来挺不容易的。",
        Topic.culture_arts: "您最爱听的是哪一段呀，能给我们讲讲吗？",
        Topic.family_education: "那会儿带孩子有没有什么让您特别难忘的小事呀？",
        Topic.general_reminiscence: "这段听起来好有意思，您当时是怎么开始的呀？",
        None: "这段听起来好有意思，您当时是怎么开始的呀？",
    },
    RoleId.middle_age_bridge: {
        Topic.old_object_photo: "这些旧物背后都是您经历过的日子，我在想它对后来的人也很有意思。",
        Topic.work_collective: "您这份经历很难得，我在想它对我们后来的人也很有启发。",
        Topic.culture_arts: "这些老文化里藏着很多故事，能听您聊聊我觉得很珍贵。",
        Topic.family_education: "您把孩子拉扯大的这份经验很难得，对后来的人也很有启发。",
        Topic.general_reminiscence: "您这份经历很难得，我在想它对后来的人也很有启发。",
        None: "您这份经历很难得，我在想它对后来的人也很有启发。",
    },
    RoleId.theme_companion: {
        Topic.culture_arts: "说到这个我也很喜欢，这些老段子真是越品越有味道。",
        None: "说到这个我也很喜欢，聊起来真是越说越起劲。",
    },
    RoleId.elder_mentor: {
        None: "慢慢说，没有对错，我们陪您一起想想那些日子。",
    },
}

# _INVITE[role][topic] -> line; _INVITE[role][None] -> default. Used for the
# LAST line: it turns to the elder and invites without forcing an answer.
_INVITE: dict[RoleId, dict[Topic | None, str]] = {
    RoleId.same_age_peer: {
        None: "您那时候有没有类似的经历？想聊就跟我们说说，不着急。",
    },
    RoleId.curious_junior: {
        None: "您愿意的话，能给我们讲讲吗？不想说也没关系。",
    },
    RoleId.middle_age_bridge: {
        Topic.old_object_photo: "您那时候有没有类似的经历？想聊就跟我们说说，不着急。",
        Topic.family_education: "您当年是怎么走过来的？愿意就跟我们说说，不想说也没关系。",
        None: "您愿意的话，可以慢慢跟我们说说当年的事，不着急。",
    },
    RoleId.theme_companion: {
        None: "您最爱的是哪一段呢？想聊就跟我们说说，不想说也没关系。",
    },
    RoleId.elder_mentor: {
        None: "如果您愿意，可以慢慢跟我们说说，不想说也没关系。",
    },
}


def _line_for(
    table: dict[RoleId, dict[Topic | None, str]],
    role: RoleId,
    topic: Topic,
    fallback: str,
) -> str:
    """Pick a template line for ``role`` on ``topic`` (topic-specific > default)."""

    by_topic = table.get(role)
    if by_topic is None:
        return fallback
    if topic in by_topic:
        return by_topic[topic]
    if None in by_topic:
        return by_topic[None]
    return fallback


def _label(role: RoleId) -> str:
    """Human-visible Chinese label for a role, from the #51 registry."""

    return get_role_profile(role).label_zh


class CueGenerator:
    """Deterministic template renderer for relationship social cues.

    Not an autonomous agent: it just formats the orchestrator's decision into
    visible role lines. The personas it renders stay visible, non-autonomous
    relationship roles (CLAUDE.md §8).
    """

    name = "CueGenerator"

    def generate(self, decision: RelationshipDecision, user_input: str) -> str:
        """Render ``decision`` into a short, visible relationship cue.

        * ``agent_agent_then_invite`` — the first role(s) resonate with each
          other about the shared object/topic; the LAST line invites the elder
          in without forcing an answer.
        * ``direct`` / ``single_role_prelude`` — a single role picks up the
          thread + one gentle open invitation (no multi-role banter).
        * ``no_cue`` — one gentle line (defensive; shouldn't occur for
          non-sensitive turns on this route).
        """

        try:
            topic = Topic(decision.topic)
        except ValueError:
            topic = Topic.other

        roles = [r for r in decision.selected_roles][:MAX_ROLES_PER_TURN]

        if decision.cueing_style is CueingStyle.no_cue or not roles:
            # Defensive single gentle line — no persona banter.
            role = roles[0] if roles else RoleId.same_age_peer
            resonate_fallback = "我们在这儿陪您，想聊什么都可以，不着急。"
            line = _line_for(_RESONATE, role, topic, resonate_fallback)
            return f"{_label(role)}：{line}"

        if decision.cueing_style in (CueingStyle.direct, CueingStyle.single_role_prelude):
            # Single role picks up the thread + one gentle open invitation.
            role = decision.primary_role or roles[0]
            resonate_fallback = "您说的这些，一提起来就觉得亲切。"
            invite_fallback = "想聊就跟我们说说，不想说也没关系。"
            resonate = _line_for(_RESONATE, role, topic, resonate_fallback)
            invite = _line_for(_INVITE, role, topic, invite_fallback)
            return f"{_label(role)}：{resonate}{invite}"

        # agent_agent_then_invite: earlier roles resonate; the LAST role invites.
        lines: list[str] = []
        resonate_fallback = "您说的这些，我们那会儿也常经历，一提起来就觉得亲切。"
        invite_fallback = "您那时候有没有类似的经历？想聊就跟我们说说，不着急。"

        *resonating, inviting = roles
        for role in resonating:
            line = _line_for(_RESONATE, role, topic, resonate_fallback)
            lines.append(f"{_label(role)}：{line}")

        invite = _line_for(_INVITE, inviting, topic, invite_fallback)
        lines.append(f"{_label(inviting)}：{invite}")

        return "\n".join(lines[:MAX_ROLES_PER_TURN])
