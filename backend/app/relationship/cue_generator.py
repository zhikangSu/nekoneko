"""Rule-based relationship-cue generator (issue #53).

Turns a :class:`RelationshipDecision` (from the deterministic
RelationshipOrchestratorAgent, #52) into a short, visible social cue for a
NON-SENSITIVE reminiscence turn. Automatic follow-up turns keep the
candidate-role set in the trace but normally let only the primary role speak.
The initial topic-card cue and explicit research conditions may render multiple
roles and add at most one low-pressure invitation.

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
from app.relationship.topic_classifier import SENSITIVE_TOPICS, Topic, classify_topic
from app.schemas.relationship import (
    CueingStyle,
    RelationshipDecision,
    RoleCueMessage,
    RoleId,
)


# The NON-SENSITIVE reminiscence topics that route to relationship_cueing.
# Explicitly EXCLUDES SENSITIVE_TOPICS (deceased_grief / health_care /
# privacy_family_conflict), loneliness_mood, and other — those stay on the
# existing companion path so grief/loneliness are never staged into persona
# banter (CLAUDE.md §7.3, non-regression guard).
CUE_ROUTE_TOPICS: frozenset[Topic] = frozenset(
    {
        Topic.study_learning,
        Topic.old_object_photo,
        Topic.work_collective,
        Topic.family_education,
        Topic.culture_arts,
        Topic.general_reminiscence,
    }
)

_RELATIONSHIP_STRAIN_MARKERS: tuple[str, ...] = (
    "不理我",
    "不搭理",
    "不跟我说话",
    "不和我说话",
    "不想跟我讲话",
    "不想和我讲话",
    "不愿意跟我",
    "不愿意和我",
    "不回我",
    "不回消息",
    "不回微信",
    "不来看我",
    "不愿意来看",
    "冷落",
    "疏远",
    "嫌我",
    "嫌弃",
    "烦我",
    "关系不好",
    "闹别扭",
    "生我的气",
    "没人理",
)


_CUE_EXCLUDED_TOPICS: frozenset[Topic] = frozenset(
    {*SENSITIVE_TOPICS, Topic.loneliness_mood}
)


_GREETING_TURN_MARKERS: tuple[str, ...] = (
    "你们好",
    "大家好",
    "你好",
    "您好",
    "早上好",
    "上午好",
    "下午好",
    "晚上好",
    "嗨",
    "哈喽",
    "hello",
)


def is_greeting_turn(text: str) -> bool:
    """Return whether the user's actual turn includes a direct greeting."""

    normalized = text.strip().lower()
    return any(marker in normalized for marker in _GREETING_TURN_MARKERS)


def is_relationship_cue_excluded(text: str) -> bool:
    """Return whether the user's own words must not be replaced by a card seed."""

    if any(marker in text for marker in _RELATIONSHIP_STRAIN_MARKERS):
        return True
    return classify_topic(text) in _CUE_EXCLUDED_TOPICS


def is_relationship_cue_turn(text: str) -> bool:
    """True only for NON-SENSITIVE reminiscence turns that should be cued.

    Sensitive topics, loneliness, and everything else stay on the companion
    path, so existing routing/tests are preserved.
    """

    if is_relationship_cue_excluded(text):
        return False

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
        Topic.study_learning: "那时候读书上学不容易，课本、教室、同学，一提起来就有那个年代的味道。",
        Topic.old_object_photo: "这样的老物件在那个年代很常见，一看见就容易带出从前的生活细节。",
        Topic.work_collective: "那个年代在单位、在大院里一块儿忙活的日子，常常带着很浓的生活气。",
        Topic.culture_arts: "这些老段子、老曲子陪伴过很多人，一响起来就很有那个年代的味道。",
        Topic.family_education: "那个年代拉扯孩子不容易，许多家庭都是一步步熬过来的。",
        Topic.general_reminiscence: "听您这么说，这段经历对您很有分量。",
        None: "听您这么说，这段经历对您很有分量。",
    },
    RoleId.curious_junior: {
        Topic.study_learning: "您那时候上学路上是什么样的呀，听起来会有很多小故事。",
        Topic.old_object_photo: "这台老电视当年是不是很稀罕呀，您还记得头一回打开它是什么时候吗？",
        Topic.work_collective: "那时候在单位是做什么活儿的呀，听起来挺不容易的。",
        Topic.culture_arts: "您最爱听的是哪一段呀？我挺想听听。",
        Topic.family_education: "那会儿带孩子有没有什么让您特别难忘的小事呀？",
        Topic.general_reminiscence: "这段听起来好有意思，您当时是怎么开始的呀？",
        None: "这段听起来好有意思，您当时是怎么开始的呀？",
    },
    RoleId.middle_age_bridge: {
        Topic.study_learning: "读书的经历常常会影响人一辈子，里面有吃苦，也有后来才明白的收获。",
        Topic.old_object_photo: "这些旧物背后都是您经历过的日子，我在想它对后来的人也很有意思。",
        Topic.work_collective: "您这份经历很难得，我在想它对我们后来的人也很有启发。",
        Topic.culture_arts: "这些老文化里藏着很多故事，一代代传下去很珍贵。",
        Topic.family_education: "您把孩子拉扯大的这份经验很难得，对后来的人也很有启发。",
        Topic.general_reminiscence: "您这份经历很难得，我在想它对后来的人也很有启发。",
        None: "您这份经历很难得，我在想它对后来的人也很有启发。",
    },
    RoleId.theme_companion: {
        Topic.culture_arts: "这个话题很有味道，这些老段子常常越品越有意思。",
        None: "这个话题听起来很有意思，可以顺着您在意的地方慢慢聊。",
    },
    RoleId.elder_mentor: {
        None: "慢慢说，没有对错，我们陪您一起想想那些日子。",
    },
}

# _INVITE[role][topic] -> line; _INVITE[role][None] -> default. Used for the
# LAST line: it turns to the elder without forcing an answer.
_INVITE: dict[RoleId, dict[Topic | None, str]] = {
    RoleId.same_age_peer: {
        None: "您那时候有没有类似的经历？不着急，想到哪儿说到哪儿。",
    },
    RoleId.curious_junior: {
        Topic.study_learning: "那时候最让您记得的一位老师、一个同学，或者一段上学路是什么样的呀？",
        None: "当时最让您记得的一件小事是什么呢？不着急，想到哪儿说到哪儿。",
    },
    RoleId.middle_age_bridge: {
        Topic.study_learning: "那时候读书上学，哪位老师、哪门课，或者哪段上学路最让您记得？",
        Topic.old_object_photo: "您那时候有没有一件一直记到现在的老物件？不着急，慢慢想。",
        Topic.family_education: "您当年带孩子时，哪件小事现在想起来最深？不着急。",
        None: "您想到哪段就说哪段，我慢慢听着。",
    },
    RoleId.theme_companion: {
        None: "哪一段现在想起来最有味道呢？",
    },
    RoleId.elder_mentor: {
        None: "您想到哪儿说到哪儿，我在这儿慢慢听。",
    },
}

# Opening lines are used only when the elder has just selected a topic card and
# has not yet shared a story. They should introduce the topic concretely without
# pretending the user already said anything.
_TOPIC_CARD_OPENING: dict[RoleId, dict[Topic | None, str]] = {
    RoleId.same_age_peer: {
        Topic.study_learning: "说到年轻时学习，课本、教室、老师和同学这些小地方，很容易带出一个年代的味道。",
        Topic.old_object_photo: "一张老照片或一件旧物，常常会把衣服、地方、天气和人情一起带出来。",
        Topic.work_collective: "说到年轻时工作，单位、车间、大院和同事这些场景，往往很有生活气。",
        Topic.culture_arts: "老电影、戏曲和老歌一响起来，很容易把地方话、街巷和从前的场面带出来。",
        Topic.family_education: "说到家庭和孩子，很多日子都藏在吃饭、接送、叮嘱这些小事里。",
        Topic.general_reminiscence: "从前的日子常常藏在一个地方、一个人、一件小事里。",
        None: "这个话题可以先从从前生活里的一个小场景慢慢展开。",
    },
    RoleId.curious_junior: {
        Topic.study_learning: "这个话题可以先从一段上学路、一位老师，或者一本课本慢慢说起。",
        Topic.old_object_photo: "这个话题可以先从照片里的一个细节，或者一件旧物的来历说起。",
        Topic.work_collective: "这个话题可以先从第一次上班、一个老同事，或者一段忙碌的日子说起。",
        Topic.culture_arts: "这个话题可以先从一段唱腔、一首老歌，或者一部老电影说起。",
        Topic.family_education: "这个话题可以先从一个家里的小场景慢慢说起。",
        Topic.general_reminiscence: "这个话题可以先从一个记得清楚的场景慢慢说起。",
        None: "这个话题可以先从一个人、一件小事，或者一个记得清楚的地方说起。",
    },
    RoleId.middle_age_bridge: {
        Topic.study_learning: "读书这件事不只是考试和功课，也常常连着后来做人做事的习惯。",
        Topic.old_object_photo: "旧物背后不只是物件，也有那个年代怎么过日子的痕迹。",
        Topic.work_collective: "工作经历里常有一代人的认真、手艺和责任感，慢慢聊会很有意思。",
        Topic.culture_arts: "这些地方文化里有一代人的审美和生活节奏，越聊越有味道。",
        Topic.family_education: "养育和教育的经验里有辛苦，也有后来才看明白的心意。",
        Topic.general_reminiscence: "有些经历放到后来再看，常常能看见那个年代留下的分量。",
        None: "有些经历放到后来再看，常常能看见那个年代留下的分量。",
    },
    RoleId.theme_companion: {
        Topic.culture_arts: "这个话题本身就有味道，唱腔、曲调和地方话都能慢慢带出回忆。",
        None: "这个话题可以慢慢铺开，不急着一下子说完。",
    },
    RoleId.elder_mentor: {
        None: "这个话题可以慢慢想，先从最容易想起的一点开始就好。",
    },
}


_TOPIC_CARD_GREETING: dict[RoleId, str] = {
    RoleId.same_age_peer: "您好呀，我们都在，见到您很高兴。",
    RoleId.curious_junior: "您好呀，您想先聊这张话题卡，还是先随意说两句都可以。",
    RoleId.middle_age_bridge: "您好，咱们不着急，先按您舒服的节奏来。",
    RoleId.elder_mentor: "您好，慢慢来，您想怎么开头都可以。",
    RoleId.theme_companion: "您好呀，这个话题什么时候想聊都可以。",
    RoleId.memory_organizer: "您好，先聊当前想说的，不急着整理。",
    RoleId.boundary_guardian: "您好，您想聊或暂时不聊都可以。",
}


# When the elder declines the current card, every active role may acknowledge
# that choice, but none may keep developing the card or ask for a story.
_TOPIC_CARD_REFUSAL: dict[RoleId, str] = {
    RoleId.same_age_peer: "好，这个我们就先不聊了，换个轻松些的也行。",
    RoleId.curious_junior: "好呀，我不再追问，您想安静一会儿也没关系。",
    RoleId.middle_age_bridge: "明白，我们把这个话题放下，按您觉得自在的来。",
    RoleId.elder_mentor: "好，不想说就先不说，您舒服最要紧。",
    RoleId.theme_companion: "好，这个话题先放下，什么时候想说别的都可以。",
    RoleId.memory_organizer: "记住了，这一段先停在这里，不再往下整理。",
    RoleId.boundary_guardian: "您的意思我们听到了，这个边界会被尊重。",
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


def _dialogue_line(line: str, *, index: int, total: int) -> str:
    """Make multi-role cue lines read like a short role-role exchange."""

    if index == 0:
        return line
    if index == total - 1:
        return f"听前面这么一说，{line}"
    return f"是啊，接着刚才说的，{line}"


class CueGenerator:
    """Deterministic template renderer for relationship social cues.

    Not an autonomous agent: it just formats the orchestrator's decision into
    visible role lines. The personas it renders stay visible, non-autonomous
    relationship roles (CLAUDE.md §8).
    """

    name = "CueGenerator"

    def generate(
        self,
        decision: RelationshipDecision,
        user_input: str,
        *,
        topic_card_opening: bool = False,
        topic_card_refusal: bool = False,
    ) -> str:
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

        if RoleId.no_ai_role in roles:
            return "我在听，您想怎么说都可以。"

        if topic_card_refusal:
            fallback = "好，这个话题先放下，按您觉得自在的来。"
            lines = [
                f"{_label(role)}：{_TOPIC_CARD_REFUSAL.get(role, fallback)}"
                for role in roles
                if role is not RoleId.no_ai_role
            ]
            return "\n".join(lines[:MAX_ROLES_PER_TURN])

        if topic_card_opening:
            if is_greeting_turn(user_input):
                greeting_fallback = "您好呀，我们都在，您想说什么都可以。"
                lines = [
                    f"{_label(role)}：{_TOPIC_CARD_GREETING.get(role, greeting_fallback)}"
                    for role in roles
                    if role is not RoleId.no_ai_role
                ]
                return "\n".join(lines[:MAX_ROLES_PER_TURN])

            opening_fallback = "这个话题可以先从从前生活里的一个小场景慢慢展开。"
            lines = [
                f"{_label(role)}：{_line_for(_TOPIC_CARD_OPENING, role, topic, opening_fallback)}"
                for role in roles
                if role is not RoleId.no_ai_role
            ]
            return "\n".join(lines[:MAX_ROLES_PER_TURN])

        if decision.cueing_style is CueingStyle.no_cue or not roles:
            # Defensive single gentle line — no persona banter.
            role = roles[0] if roles else RoleId.same_age_peer
            resonate_fallback = "我们在这儿陪您，想聊什么都可以，不着急。"
            line = _line_for(_RESONATE, role, topic, resonate_fallback)
            return f"{_label(role)}：{line}"

        if decision.cueing_style is CueingStyle.direct:
            # Direct turns answer or acknowledge without mechanically appending
            # a question. The real provider may ask one only when it is useful.
            role = decision.primary_role or roles[0]
            resonate_fallback = "听您这么说，这件事对您有它自己的分量。"
            resonate = _line_for(_RESONATE, role, topic, resonate_fallback)
            return f"{_label(role)}：{resonate}"

        if decision.cueing_style is CueingStyle.single_role_prelude:
            # An explicit prelude may include one low-pressure invitation.
            role = decision.primary_role or roles[0]
            resonate_fallback = "听您这么说，这件事对您有它自己的分量。"
            resonate = _line_for(_RESONATE, role, topic, resonate_fallback)
            if not decision.allow_follow_up:
                return f"{_label(role)}：{resonate}"
            invite_fallback = "您想到哪儿说到哪儿，我慢慢听。"
            invite = _line_for(_INVITE, role, topic, invite_fallback)
            return f"{_label(role)}：{resonate}{invite}"

        # agent_agent_then_invite: earlier roles resonate; the LAST role invites.
        lines: list[str] = []
        resonate_fallback = "听您这么说，这段经历对您很有分量。"
        invite_fallback = "您那时候有没有类似的经历？不着急，想到哪儿说到哪儿。"

        if not decision.allow_follow_up:
            lines = []
            for index, role in enumerate(roles):
                line = _line_for(_RESONATE, role, topic, resonate_fallback)
                lines.append(
                    f"{_label(role)}："
                    f"{_dialogue_line(line, index=index, total=len(roles))}"
                )
            return "\n".join(lines[:MAX_ROLES_PER_TURN])

        *resonating, inviting = roles
        total = len(roles)
        for index, role in enumerate(resonating):
            line = _line_for(_RESONATE, role, topic, resonate_fallback)
            lines.append(f"{_label(role)}：{_dialogue_line(line, index=index, total=total)}")

        invite = _line_for(_INVITE, inviting, topic, invite_fallback)
        lines.append(
            f"{_label(inviting)}：{_dialogue_line(invite, index=total - 1, total=total)}"
        )

        return "\n".join(lines[:MAX_ROLES_PER_TURN])


def role_messages_from_cue(cue_text: str, roles: list[RoleId]) -> list[RoleCueMessage]:
    """Split a visible cue template into structured role bubbles."""

    role_by_label = {
        get_role_profile(role).label_zh: role
        for role in roles
        if role is not RoleId.no_ai_role
    }
    messages: list[RoleCueMessage] = []

    for raw_line in cue_text.splitlines():
        line = raw_line.strip()
        if "：" not in line:
            continue
        label, text = line.split("：", 1)
        role = role_by_label.get(label)
        if role is None:
            continue
        text = text.strip()
        if not text:
            continue
        messages.append(RoleCueMessage(role_id=role, role_label=label, text=text))

    return messages[:MAX_ROLES_PER_TURN]
