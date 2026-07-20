"""Graph nodes (issue #5).

Each node takes the shared ``GraphState`` and the ``GraphDeps`` (agent / guard
instances) and mutates the state, appending trace steps tagged by kind so the
Agent / Tool / Guard distinction stays visible.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.agents.companion import CompanionAgent
from app.agents.coordinator import CoordinatorAgent
from app.agents.relationship_orchestrator import RelationshipOrchestratorAgent
from app.agents.safety_critic import SafetyCriticAgent
from app.core.constants import TraceEntryKind
from app.graph.state import GraphState
from app.relationship.cue_generator import (
    CueGenerator,
    is_greeting_turn,
    is_relationship_cue_excluded,
    is_relationship_cue_turn,
    role_messages_from_cue,
)
from app.relationship.role_profiles import MAX_ROLES_PER_TURN, get_role_profile
from app.relationship.turn_intent import (
    PresenceQuestionKind,
    classify_presence_question,
    presence_reply_matches,
)
from app.schemas.memory_candidate import MemoryTriageAction
from app.schemas.relationship import (
    ElderControlAction,
    OrchestrationInput,
    RoleCueMessage,
    RoleId,
    RoleSelectionMode,
    StudyCondition,
)
from app.schemas.trace import TraceStep
from app.stores.memory_card_store import MemoryCardStore
from app.tools.info_retrieval import InfoRetrievalTool
from app.tools.input_rule_guard import InputRuleGuard
from app.tools.memory_card_tool import MemoryCardTool
from app.tools.memory_candidate_extractor import MemoryCandidateExtractor
from app.tools.memory_triage_policy import MemoryTriagePolicy
from app.tools.memory_tool import MemoryTool
from app.tools.output_rule_guard import OutputRuleGuard
from app.tools.reminder_tool import ReminderTool


@dataclass
class GraphDeps:
    input_guard: InputRuleGuard
    output_guard: OutputRuleGuard
    coordinator: CoordinatorAgent
    companion: CompanionAgent
    safety_critic: SafetyCriticAgent
    memory_tool: MemoryTool
    memory_card_tool: MemoryCardTool
    memory_card_store: MemoryCardStore
    memory_candidate_extractor: MemoryCandidateExtractor
    memory_triage_policy: MemoryTriagePolicy
    reminder_tool: ReminderTool
    info_retrieval: InfoRetrievalTool
    relationship_orchestrator: RelationshipOrchestratorAgent
    cue_generator: CueGenerator


_TOPIC_CARD_CUE_TEXT: dict[str, str] = {
    "T01": "年轻时学习读书上学学校老师同学",
    "T02": "年轻时工作上班",
    "T03": "家庭孩子教育",
    "T04": "以前的老朋友老邻居集体生活",
    "T05": "老照片旧物老电视",
    "T06": "老电影戏曲粤剧老歌地方文化",
    "T07": "重要人生选择当年",
    "T08": "人生遗憾后悔",
    "T09": "已故亲友老伴去世故人",
    "T10": "身体健康照护吃药",
    "T11": "新技术手机网络新生活",
    "T12": "孤独陪伴一个人日常心情",
}

_GENERIC_TOPIC_CARD_MARKERS: tuple[str, ...] = (
    "聊这个",
    "讲这个",
    "说这个",
    "这个话题",
    "这张卡",
    "这张照片",
    "这件东西",
    "这个吧",
    "开始吧",
    "可以",
    "好啊",
    "好呀",
    "继续",
)

_TOPIC_CARD_QUESTION_MARKERS: tuple[str, ...] = (
    "什么",
    "怎么",
    "为什么",
    "为啥",
    "哪",
    "谁",
    "吗",
    "呢",
    "？",
    "?",
)

_TOPIC_CARD_REFUSAL_MARKERS: tuple[str, ...] = (
    "不想聊",
    "不太想聊",
    "不想说",
    "不太想说",
    "先不聊",
    "不聊了",
    "别聊",
    "别提",
    "不要聊",
    "算了",
    "换个话题",
    "换一个话题",
    "不感兴趣",
    "没兴趣",
    "改天再聊",
    "下次再聊",
)


def _topic_card_seed_text(state: GraphState) -> str:
    if not state.topic_id and not state.topic_label:
        return ""
    if state.topic_id:
        mapped = _TOPIC_CARD_CUE_TEXT.get(state.topic_id.upper())
        if mapped:
            return mapped
    return state.topic_label or ""


def _can_topic_card_seed_cue(state: GraphState) -> bool:
    text = state.user_input.strip()
    if len(text) > 18:
        return False
    if _is_topic_card_refusal_turn(state):
        return False
    if is_relationship_cue_excluded(text):
        return False
    # Topic-card metadata accompanies every message in the ambient scene.  It
    # must only seed the deterministic opener for a real acceptance turn, not
    # when a greeting happens to contain ``好啊`` or the user asks a question.
    if is_greeting_turn(text) or classify_presence_question(text) is not None:
        return False
    if any(marker in text for marker in _TOPIC_CARD_QUESTION_MARKERS):
        return False
    return any(marker in text for marker in _GENERIC_TOPIC_CARD_MARKERS)


def _is_topic_card_refusal_turn(state: GraphState) -> bool:
    text = state.user_input.strip()
    if not _topic_card_seed_text(state):
        return False
    if is_relationship_cue_excluded(text):
        return False
    return any(marker in text for marker in _TOPIC_CARD_REFUSAL_MARKERS)


def _is_topic_card_start_turn(state: GraphState) -> bool:
    return bool(_topic_card_seed_text(state) and _can_topic_card_seed_cue(state))


def _relationship_cue_input(state: GraphState) -> str:
    if is_relationship_cue_turn(state.user_input):
        return state.user_input
    seed = _topic_card_seed_text(state)
    if _is_topic_card_start_turn(state) or _is_topic_card_refusal_turn(state):
        return f"{seed}。{state.user_input}"
    return state.user_input


def _should_route_relationship_cue(state: GraphState) -> bool:
    if state.elder_control_action in {
        ElderControlAction.pause_roles,
        ElderControlAction.stop_reminiscence,
    }:
        return False
    if state.study_condition == StudyCondition.c1_direct_question:
        return False
    if _is_topic_card_refusal_turn(state):
        return True
    if is_relationship_cue_turn(state.user_input):
        return True
    seed = _topic_card_seed_text(state)
    return bool(_is_topic_card_start_turn(state) and is_relationship_cue_turn(seed))


def _append_companion_trace(
    state: GraphState,
    deps: GraphDeps,
    result,
    *,
    extra_detail: dict | None = None,
) -> None:
    detail = {
        "mode": result.mode.value,
        "companion_display_name": result.companion_display_name,
        "named_by_user": result.named_by_user,
        "prompt_version": deps.companion.prompt_version,
        "llm_generation": result.llm_generation,
        "conversation_history_used": state.conversation_history_used,
        "conversation_history_count": len(state.conversation_history),
    }
    if extra_detail:
        detail.update(extra_detail)
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.companion.name,
            summary=_companion_trace_summary(result, extra_detail),
            detail=detail,
        )
    )


def _companion_trace_summary(result, extra_detail: dict | None = None) -> str:
    detail = extra_detail or {}
    role_labels = detail.get("role_labels") or []
    style = "情绪承接优先" if result.mode.value == "role_first" else "中性助理对照"
    if role_labels:
        if detail.get("manual_role_style"):
            source = "用户自选"
        elif detail.get("context_role_style"):
            source = "延续当前场景"
        else:
            source = "系统分配"
        return f"{style}；{source}关系角色「{'、'.join(role_labels)}」"
    if detail.get("manual_no_ai_role"):
        return (
            f"{style}；用户选择不使用关系角色，"
            "由用户命名的 CompanionAgent 轻量回应"
        )
    return result.trace_summary()


def _manual_role_ids_for_talk(state: GraphState) -> list[RoleId]:
    if state.role_selection_mode is not RoleSelectionMode.manual:
        return []
    if RoleId.no_ai_role in state.selected_role_ids:
        return []

    seen: set[RoleId] = set()
    role_ids: list[RoleId] = []
    for role_id in state.selected_role_ids:
        if role_id is RoleId.no_ai_role or role_id in seen:
            continue
        role_ids.append(role_id)
        seen.add(role_id)
    return role_ids[:MAX_ROLES_PER_TURN]


def _role_style_context_for_profiles(
    profiles,
    source: str,
    *,
    topic_card_refusal: bool = False,
    direct_turn: bool = False,
) -> str:
    role_lines = []
    for profile in profiles:
        boundary = "；".join(profile.boundary_rules[:3])
        role_lines.append(
            f"- {profile.role_id.value} / {profile.label_zh}: "
            f"{profile.relationship_function}；说话方式：{profile.speaking_style}；"
            f"边界：{boundary}"
        )

    context = f"{source}，请只使用这些角色的关系视角。\n" + "\n".join(role_lines)
    if topic_card_refusal:
        context += (
            "\n用户已经明确拒绝当前话题。这是边界确认轮次：每个角色只需用自己的语气"
            "简短确认已经听见并尊重用户的选择。不得继续展开被拒绝的话题，不得追问原因，"
            "不得要求用户讲故事，不得提出问题，也不要立刻指定另一个话题。"
        )
        if len(profiles) > 1:
            labels = "、".join(profile.label_zh for profile in profiles)
            context += (
                f"请严格输出 {len(profiles)} 行，顺序为：{labels}。"
                "每行必须以完整角色名和中文冒号开头。每位角色分别回应，不要合并成总回复；"
                "后面的角色可以自然接住前面的意思，但最后一位也不要把话题递回给用户。"
            )
        return context

    if len(profiles) == 1:
        label = profiles[0].label_zh
        context += (
            f"\n输出格式要求：本轮只有一个可见关系角色。请严格只输出 1 行，"
            f"并以完整角色名“{label}：”开头。不要退回“陪伴 AI”或其他角色名，"
            "不要解释角色选择。"
        )
    elif len(profiles) > 1:
        labels = "、".join(profile.label_zh for profile in profiles)
        context += (
            "\n输出格式要求：本轮有多个可见关系角色，必须让每个角色分别说一句。"
            f"请严格输出 {len(profiles)} 行，顺序为：{labels}。"
            "每行必须以完整角色名和中文冒号开头，例如“同龄共鸣者：...”。"
        )
        if direct_turn:
            context += (
                "这是已有多人场景的继续轮次。每位角色都应围绕用户本轮的具体内容直接接话，"
                "不要重新表演一段话题开场，不要强制把话题递回用户，也不必提出问题。"
            )
        else:
            context += (
                "这几行要形成角色之间的短对话：第一位先接住用户的话或话题，"
                "第二位必须接上一位的意思继续说，最后一位再把话题自然递给用户。"
            )
        context += (
            "不要让每个角色都独立重复用户的话，不要把多个角色合并成一个总回复，"
            "不要写总括句、主持人话术或角色选择解释。"
            "角色之间接话不要使用“您们”这类生硬称呼，可用“刚才说的”或“听前面这么一说”。"
        )
    context += "\n回复正文中不要使用“您们”这个称呼。"
    return context


def _manual_role_style_context(state: GraphState) -> tuple[str | None, dict | None]:
    if state.role_selection_mode is not RoleSelectionMode.manual:
        return None, None

    requested_role_ids = [role_id.value for role_id in state.selected_role_ids]
    state.requested_relationship_roles = requested_role_ids
    state.relationship_role_selection_mode = RoleSelectionMode.manual.value

    if RoleId.no_ai_role in state.selected_role_ids:
        state.candidate_relationship_roles = []
        state.selected_relationship_roles = []
        state.silent_relationship_roles = []
        state.relationship_primary_role = None
        state.relationship_allow_follow_up = False
        state.relationship_follow_up_reason = (
            "用户选择不使用关系角色，不追加研究式追问。"
        )
        return None, {
            "manual_role_style": False,
            "manual_no_ai_role": True,
            "requested_role_ids": requested_role_ids,
            "candidate_roles": [],
            "selected_roles": [],
            "silent_roles": [],
            "role_labels": [],
        }

    role_ids = _manual_role_ids_for_talk(state)
    if not role_ids:
        return None, {
            "manual_role_style": False,
            "manual_no_ai_role": False,
            "requested_role_ids": requested_role_ids,
            "selected_roles": [],
            "role_labels": [],
        }

    profiles = [get_role_profile(role_id) for role_id in role_ids]
    state.candidate_relationship_roles = [
        profile.role_id.value for profile in profiles
    ]
    state.selected_relationship_roles = [profile.role_id.value for profile in profiles]
    state.silent_relationship_roles = []
    state.relationship_primary_role = profiles[0].role_id.value
    state.relationship_allow_follow_up = True
    state.relationship_follow_up_reason = (
        "用户显式选择关系角色，允许至多一个低压力邀请。"
    )
    context = _role_style_context_for_profiles(
        profiles,
        "用户本轮手动选择了这些关系角色",
    )
    return context, {
        "manual_role_style": True,
        "manual_no_ai_role": False,
        "requested_role_ids": requested_role_ids,
        "candidate_roles": [profile.role_id.value for profile in profiles],
        "selected_roles": [profile.role_id.value for profile in profiles],
        "silent_roles": [],
        "role_labels": [profile.label_zh for profile in profiles],
    }


def _auto_role_style_context(state: GraphState, deps: GraphDeps) -> tuple[str | None, dict | None]:
    if state.role_selection_mode is RoleSelectionMode.manual:
        return None, None

    decision = deps.relationship_orchestrator.orchestrate(
        OrchestrationInput(
            user_input=state.user_input,
            memory_context=list(state.memory_context or []),
            recent_emotion_or_tone=None,
            user_role_preferences=None,
            role_selection_mode=RoleSelectionMode.auto,
            selected_role_ids=[],
            context_role_ids=state.context_role_ids,
            risk_flags={
                "risk_level": state.risk.level.value,
                "category": state.risk.category,
                "matched_terms": state.risk.matched_terms,
            },
        )
    )
    role_ids = [
        role_id
        for role_id in decision.selected_roles
        if role_id is not RoleId.no_ai_role
    ][:MAX_ROLES_PER_TURN]
    state.relationship_role_selection_mode = RoleSelectionMode.auto.value
    state.relationship_role_selection_source = decision.role_selection_source.value
    state.interaction_intent = decision.interaction_intent.value
    state.candidate_relationship_roles = [
        role_id.value for role_id in decision.candidate_roles
    ]
    state.selected_relationship_roles = [role_id.value for role_id in role_ids]
    state.silent_relationship_roles = [
        role_id.value for role_id in decision.silent_roles
    ]
    state.relationship_primary_role = (
        decision.primary_role.value
        if decision.primary_role in role_ids
        else (role_ids[0].value if role_ids else None)
    )
    state.relationship_topic = decision.topic
    state.relationship_boundary_notes = list(decision.boundary_notes)
    state.cueing_style = decision.cueing_style.value
    state.relationship_allow_follow_up = decision.allow_follow_up
    state.relationship_follow_up_reason = decision.follow_up_reason
    context_role_style = decision.role_selection_source.value == "visible_context"
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.relationship_orchestrator.name,
            summary=(
                f"普通聊天关系策略：{decision.trace_visible_summary}"
            ),
            detail={
                "auto_role_style": bool(role_ids),
                "context_role_style": context_role_style,
                "interaction_intent": decision.interaction_intent.value,
                "topic": decision.topic,
                "role_selection_mode": RoleSelectionMode.auto.value,
                "role_selection_source": decision.role_selection_source.value,
                "context_role_ids": [role_id.value for role_id in state.context_role_ids],
                "candidate_roles": [
                    role_id.value for role_id in decision.candidate_roles
                ],
                "selected_roles": [role_id.value for role_id in role_ids],
                "silent_roles": [
                    role_id.value for role_id in decision.silent_roles
                ],
                "primary_role": state.relationship_primary_role,
                "cueing_style": decision.cueing_style.value,
                "allow_follow_up": decision.allow_follow_up,
                "follow_up_reason": decision.follow_up_reason,
                "role_selection_reason": decision.role_selection_reason,
                "boundary_notes": decision.boundary_notes,
                "role_trace": decision.role_trace,
                "topic_trace": decision.topic_trace,
                "memory_trace": decision.memory_trace,
                "boundary_trace": decision.boundary_trace,
            },
        )
    )
    if not role_ids:
        return None, {
            "auto_role_style": False,
            "context_role_style": False,
            "interaction_intent": decision.interaction_intent.value,
            "role_selection_source": decision.role_selection_source.value,
            "candidate_roles": [role.value for role in decision.candidate_roles],
            "selected_roles": [role.value for role in decision.selected_roles],
            "silent_roles": [role.value for role in decision.silent_roles],
            "role_labels": [],
        }

    profiles = [get_role_profile(role_id) for role_id in role_ids]
    context = _role_style_context_for_profiles(
        profiles,
        (
            "当前场景已经显示这些关系角色，本轮继续由他们接话"
            if context_role_style
            else "系统本轮自动分配了这些关系角色"
        ),
        direct_turn=decision.cueing_style.value == "direct",
    )
    return context, {
        "auto_role_style": True,
        "context_role_style": context_role_style,
        "manual_role_style": False,
        "manual_no_ai_role": False,
        "requested_role_ids": [],
        "interaction_intent": decision.interaction_intent.value,
        "role_selection_source": decision.role_selection_source.value,
        "candidate_roles": [role.value for role in decision.candidate_roles],
        "selected_roles": [profile.role_id.value for profile in profiles],
        "silent_roles": [role.value for role in decision.silent_roles],
        "role_labels": [profile.label_zh for profile in profiles],
    }


def _companion_role_style_context(
    state: GraphState,
    deps: GraphDeps,
) -> tuple[str | None, dict | None]:
    if (
        state.study_condition is StudyCondition.c1_direct_question
        or state.elder_control_action
        in {ElderControlAction.pause_roles, ElderControlAction.stop_reminiscence}
    ):
        return None, None
    if is_relationship_cue_excluded(state.user_input):
        if state.role_selection_mode is RoleSelectionMode.manual:
            return None, None
        _, trace = _auto_role_style_context(state, deps)
        if trace:
            trace = {
                **trace,
                "auto_role_style": False,
                "selected_roles": [],
                "role_labels": [],
            }
        return None, trace
    if state.role_selection_mode is RoleSelectionMode.manual:
        context, trace = _manual_role_style_context(state)
    else:
        context, trace = _auto_role_style_context(state, deps)

    presence_kind = classify_presence_question(state.user_input)
    if presence_kind is None:
        return context, trace

    direct_instruction = (
        "\n用户本轮是在直接询问你们此刻在做什么、是谁，或能否听见。"
        "必须先按字面直接回答当前问题；如有短期对话历史，再据此说明刚才在聊什么。"
        "不要把问题改写成回忆访谈，不要假设用户已经讲过某段经历，"
        "不要使用“您说的这些”“最让您记得”“当时的一件小事”等泛化追问。"
    )
    context = f"{context or ''}{direct_instruction}"
    trace = {
        **(trace or {}),
        "direct_presence_question": True,
        "direct_presence_question_kind": presence_kind,
    }
    return context, trace


def _role_ids_for_structured_reply(role_style_trace: dict | None) -> list[RoleId]:
    if not role_style_trace:
        return []

    role_ids: list[RoleId] = []
    for raw_role_id in role_style_trace.get("selected_roles") or []:
        try:
            role_id = RoleId(raw_role_id)
        except ValueError:
            continue
        if role_id is RoleId.no_ai_role:
            continue
        role_ids.append(role_id)
    return role_ids


_INCOMPLETE_ROLE_REPLY_SUFFIXES = (
    "，",
    "、",
    "；",
    "：",
    "就",
    "把",
    "被",
    "在",
    "和",
    "跟",
    "让",
    "会",
    "要",
    "想",
    "听着",
    "我们",
    "咱们",
)

_TOPIC_REFUSAL_PRESSURE_MARKERS = (
    "您愿意",
    "您说说",
    "您讲讲",
    "先从",
    "最让您",
    "还记得",
)

_FABRICATED_LIVED_EXPERIENCE_MARKERS = (
    "我们那会儿",
    "我们那时候",
    "我们那代人",
    "我那会儿",
    "我小时候",
    "我年轻时",
    "我也经历过",
    "我家以前",
    "听着长大",
)

_ROLE_REPLY_TEXT_REPLACEMENTS = (
    ("您们", "大家"),
)

_GREETING_ACKNOWLEDGEMENT_MARKERS = (
    "你好",
    "您好",
    "问好",
    "大家好",
    "早上好",
    "上午好",
    "下午好",
    "晚上好",
    "嗨",
    "哈喽",
    "hello",
    "在呢",
    "听见您",
    "很高兴见到",
)


def _visible_role_ids(expected_roles: list[RoleId]) -> list[RoleId]:
    return [
        role_id
        for role_id in expected_roles[:MAX_ROLES_PER_TURN]
        if role_id is not RoleId.no_ai_role
    ]


def _normalize_role_reply_text(text: str) -> tuple[str, list[str]]:
    normalized = text
    replaced_terms: list[str] = []
    for source, replacement in _ROLE_REPLY_TEXT_REPLACEMENTS:
        if source not in normalized:
            continue
        normalized = normalized.replace(source, replacement)
        replaced_terms.append(source)
    return normalized, replaced_terms


def _order_role_messages(
    messages: list[RoleCueMessage],
    expected_roles: list[RoleId],
) -> list[RoleCueMessage]:
    expected = _visible_role_ids(expected_roles)
    by_role: dict[RoleId, list[RoleCueMessage]] = {role_id: [] for role_id in expected}
    for message in messages:
        if message.role_id in by_role:
            by_role[message.role_id].append(message)

    if len(messages) != len(expected) or any(
        len(by_role[role_id]) != 1 for role_id in expected
    ):
        return messages
    return [by_role[role_id][0] for role_id in expected]


def _render_role_messages(messages: list[RoleCueMessage]) -> str:
    return "\n".join(
        f"{message.role_label}：{message.text.strip()}" for message in messages
    )


def _prepare_role_reply(
    reply_text: str,
    expected_roles: list[RoleId],
    *,
    topic_card_refusal: bool = False,
    require_greeting_acknowledgement: bool = False,
    direct_presence_question_kind: PresenceQuestionKind | None = None,
) -> tuple[str, list[RoleCueMessage], bool, str | None, list[str]]:
    normalized_text, replaced_terms = _normalize_role_reply_text(reply_text)
    messages = role_messages_from_cue(normalized_text, expected_roles)
    messages = _order_role_messages(messages, expected_roles)
    accepted, rejection_reason = _role_messages_validation(
        messages,
        expected_roles,
        topic_card_refusal=topic_card_refusal,
        require_greeting_acknowledgement=require_greeting_acknowledgement,
        direct_presence_question_kind=direct_presence_question_kind,
    )
    if accepted:
        normalized_text = _render_role_messages(messages)
    return normalized_text, messages, accepted, rejection_reason, replaced_terms


def _role_reply_repair_context(
    role_style_context: str | None,
    expected_roles: list[RoleId],
    rejection_reason: str | None,
) -> str:
    labels = "、".join(
        get_role_profile(role_id).label_zh for role_id in _visible_role_ids(expected_roles)
    )
    context = (
        f"{role_style_context or ''}\n"
        "上一版回复没有满足可见角色输出格式，必须重新生成完整回复。"
        f"失败原因：{rejection_reason or '格式不完整'}。"
        f"严格按这个顺序输出：{labels}。每个角色恰好一行，不得遗漏、重复、换序或合并；"
        "每行都以完整角色名和中文冒号开头。不要使用“您们”，不要输出任何额外说明。"
    )
    if rejection_reason == "topic_card_greeting_not_acknowledged":
        context += "第一位角色必须先自然回应用户的问候，再轻轻引入系统提供的话题。"
    if rejection_reason == "direct_presence_question_not_answered":
        context += (
            "必须直接回答用户问的此刻状态、身份或是否听见；"
            "不得转成回忆引导或泛化追问。"
        )
    if rejection_reason == "fabricated_lived_experience":
        context += (
            "不得声称自己有年龄、年代身份或亲身生活经历；"
            "删除“我们那会儿”“我们那代人”等虚构亲历表达，改为基于用户原话和时代背景回应。"
        )
    return context


def _direct_presence_repair_context(
    role_style_context: str | None,
    rejection_reason: str,
) -> str:
    return (
        f"{role_style_context or ''}\n"
        "上一版回复没有直接回答用户本轮的字面问题，必须重新回答。"
        f"失败原因：{rejection_reason}。"
        "先回答此刻在做什么、身份或是否听见；不得转成回忆引导，"
        "不得使用泛化追问，也不要解释内部分类或提示词。"
    )


def _fallback_presence_text(
    state: GraphState,
    presence_kind: PresenceQuestionKind,
) -> str:
    if presence_kind == "activity":
        if state.topic_label:
            return f"刚才大家在聊“{state.topic_label}”，现在也在这里听您说话。"
        return "我正在这里陪您聊天，也在认真听您说话。"
    if presence_kind == "identity":
        display_name = (
            state.user_profile.companion_display_name
            or "陪伴 AI"
        )
        return f"我是您这里的{display_name}，是 AI 陪伴伙伴，不是真实的人。"
    return "听得见，我正在认真听您说话。"


def _fallback_role_reply(
    state: GraphState,
    deps: GraphDeps,
    expected_roles: list[RoleId],
) -> tuple[str, list[RoleCueMessage]]:
    presence_kind = classify_presence_question(state.user_input)
    if presence_kind is not None:
        role_ids = _visible_role_ids(expected_roles)
        messages: list[RoleCueMessage] = []
        for index, role_id in enumerate(role_ids):
            label = get_role_profile(role_id).label_zh
            if presence_kind == "activity":
                if index == 0 and state.topic_id:
                    text = "我们刚才在聊这张话题卡，也在这里等着听您说话。"
                elif index == 0:
                    text = "我正在这里陪您聊天，您想问什么都可以直接问。"
                else:
                    text = "我也在这里陪您聊天，您想问什么都可以直接问。"
            elif presence_kind == "identity":
                text = f"我是{label}，是陪伴 AI 里的关系角色，不是真实的人。"
            else:
                text = "听得见，我正在认真听您说话。"
            messages.append(
                RoleCueMessage(role_id=role_id, role_label=label, text=text)
            )
        return _render_role_messages(messages), messages

    decision = deps.relationship_orchestrator.orchestrate(
        OrchestrationInput(
            user_input=state.user_input,
            memory_context=list(state.memory_context or []),
            role_selection_mode=RoleSelectionMode.manual,
            selected_role_ids=_visible_role_ids(expected_roles),
            risk_flags={
                "risk_level": state.risk.level.value,
                "category": state.risk.category,
                "matched_terms": state.risk.matched_terms,
            },
        )
    )
    fallback_text = deps.cue_generator.generate(decision, state.user_input)
    prepared_text, messages, _, _, _ = _prepare_role_reply(
        fallback_text,
        expected_roles,
    )
    return prepared_text, messages


def _role_messages_validation(
    messages: list[RoleCueMessage],
    expected_roles: list[RoleId],
    *,
    topic_card_refusal: bool = False,
    require_greeting_acknowledgement: bool = False,
    direct_presence_question_kind: PresenceQuestionKind | None = None,
) -> tuple[bool, str | None]:
    expected = _visible_role_ids(expected_roles)
    expected_count = len(expected)
    if expected_count > 0 and len(messages) < expected_count:
        return False, f"expected_{expected_count}_role_lines_got_{len(messages)}"

    actual = [message.role_id for message in messages]
    if actual != expected:
        if topic_card_refusal:
            return False, "topic_refusal_role_order_mismatch"
        return False, "role_order_or_membership_mismatch"

    for message in messages:
        text = message.text.strip()
        if len(text) < 8:
            return False, "role_line_too_short"
        if text.endswith(_INCOMPLETE_ROLE_REPLY_SUFFIXES):
            return False, "role_line_looks_incomplete"
        if topic_card_refusal and (
            "？" in text
            or "?" in text
            or any(marker in text for marker in _TOPIC_REFUSAL_PRESSURE_MARKERS)
        ):
            return False, "topic_refusal_reply_pressures_user"
    if require_greeting_acknowledgement:
        combined_text = "\n".join(message.text for message in messages).lower()
        if not any(
            marker in combined_text for marker in _GREETING_ACKNOWLEDGEMENT_MARKERS
        ):
            return False, "topic_card_greeting_not_acknowledged"
    if direct_presence_question_kind is not None:
        combined_text = "\n".join(message.text for message in messages)
        if not presence_reply_matches(combined_text, direct_presence_question_kind):
            return False, "direct_presence_question_not_answered"
    combined_text = "\n".join(message.text for message in messages)
    if any(
        marker in combined_text
        for marker in _FABRICATED_LIVED_EXPERIENCE_MARKERS
    ):
        return False, "fabricated_lived_experience"
    return True, None


def input_guard_node(state: GraphState, deps: GraphDeps) -> GraphState:
    result = deps.input_guard.run(state.user_input)
    state.risk = result.classification
    state.guards.append(
        TraceStep(
            kind=TraceEntryKind.guard,
            name=deps.input_guard.name,
            summary=result.summary,
            detail={
                "risk_level": result.classification.level.value,
                "category": result.classification.category,
                "matched_terms": result.classification.matched_terms,
            },
        )
    )
    return state


def coordinator_node(state: GraphState, deps: GraphDeps) -> GraphState:
    decision = deps.coordinator.decide(
        classification=state.risk,
        has_state_event=state.has_state_event,
        reminder_intent=deps.reminder_tool.is_reminder_request(state.user_input),
        retrieval_intent=deps.info_retrieval.is_retrieval_query(state.user_input),
        reminiscence_cue_intent=_should_route_relationship_cue(state),
    )
    state.route = decision.route
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.coordinator.name,
            summary=f"route = {decision.route.value}：{decision.reason}",
            detail={"route": decision.route.value, "reason": decision.reason},
        )
    )
    return state


def memory_read_node(state: GraphState, deps: GraphDeps) -> GraphState:
    if state.memory_scope == "session_only":
        state.memory_context = []
        state.memory_used = False
        state.tools.append(
            TraceStep(
                kind=TraceEntryKind.memory,
                name=deps.memory_tool.name,
                summary="当前窗口使用独立上下文，未读取长期记忆",
                detail={"memory_scope": state.memory_scope},
            )
        )
        return state

    # Master privacy switch from the profile/onboarding (#21): when the user has
    # turned memory off, never read it.
    if not state.user_profile.memory_enabled:
        state.memory_context = []
        state.memory_used = False
        state.tools.append(
            TraceStep(
                kind=TraceEntryKind.memory,
                name=deps.memory_tool.name,
                summary="记忆功能已关闭（memory_enabled=false），未读取",
                detail={"memory_enabled": False},
            )
        )
        return state

    entries = deps.memory_tool.load_context(state.user_id)
    contents = [e.content for e in entries]
    state.memory_context = contents
    state.memory_used = len(contents) > 0
    state.tools.append(
        TraceStep(
            kind=TraceEntryKind.memory,
            name=deps.memory_tool.name,
            summary=(
                f"读取 {len(contents)} 条记忆：{('、'.join(contents))[:60]}"
                if contents
                else "未找到长期记忆"
            ),
            detail={"count": len(contents), "memories": contents},
        )
    )
    return state


def retrieval_node(state: GraphState, deps: GraphDeps) -> GraphState:
    result = deps.info_retrieval.retrieve(state.user_input)
    state.retrieval_used = True
    state.retrieval_context = result.summary if result.found else None
    state.tools.append(
        TraceStep(
            kind=TraceEntryKind.retrieval,
            name=deps.info_retrieval.name,
            summary=(
                f"调用外部检索（{result.query_kind}，来源 {result.source}"
                f"{'，mock' if result.mock else ''}）：{result.summary[:40]}"
            ),
            detail={
                "query_kind": result.query_kind,
                "source": result.source,
                "mock": result.mock,
                "found": result.found,
            },
        )
    )
    return state


def companion_node(state: GraphState, deps: GraphDeps) -> GraphState:
    state.conversation_history_used = bool(state.conversation_history)
    role_style_context, role_style_trace = _companion_role_style_context(state, deps)
    result = deps.companion.respond(
        message=state.user_input,
        mode=state.mode,
        companion_display_name=state.user_profile.companion_display_name,
        memory_context=state.memory_context,
        retrieval_context=state.retrieval_context,
        role_style_context=role_style_context,
        conversation_history=state.conversation_history,
    )
    structured_role_ids = _role_ids_for_structured_reply(role_style_trace)
    direct_presence_question_kind = (
        role_style_trace.get("direct_presence_question_kind")
        if role_style_trace
        else None
    )
    role_reply_detail: dict = {}
    if structured_role_ids and deps.companion.llm_provider_name != "fake":
        (
            prepared_text,
            prepared_messages,
            role_reply_accepted,
            rejection_reason,
            normalized_terms,
        ) = _prepare_role_reply(
            result.reply_text,
            structured_role_ids,
            direct_presence_question_kind=direct_presence_question_kind,
        )
        initial_rejection_reason = rejection_reason
        retry_used = False
        retry_accepted = False

        if not role_reply_accepted and deps.companion.llm_provider_name != "fake":
            retry_used = True
            result = deps.companion.respond(
                message=state.user_input,
                mode=state.mode,
                companion_display_name=state.user_profile.companion_display_name,
                memory_context=state.memory_context,
                retrieval_context=state.retrieval_context,
                role_style_context=_role_reply_repair_context(
                    role_style_context,
                    structured_role_ids,
                    rejection_reason,
                ),
                conversation_history=state.conversation_history,
            )
            (
                prepared_text,
                prepared_messages,
                role_reply_accepted,
                rejection_reason,
                retry_normalized_terms,
            ) = _prepare_role_reply(
                result.reply_text,
                structured_role_ids,
                direct_presence_question_kind=direct_presence_question_kind,
            )
            normalized_terms.extend(retry_normalized_terms)
            retry_accepted = role_reply_accepted

        fallback_used = not role_reply_accepted
        if fallback_used:
            prepared_text, prepared_messages = _fallback_role_reply(
                state,
                deps,
                structured_role_ids,
            )

        state.draft_reply = prepared_text
        state.role_messages = prepared_messages
        role_reply_detail = {
            "llm_role_reply_accepted": role_reply_accepted,
            "llm_role_reply_initial_rejection_reason": initial_rejection_reason,
            "llm_role_reply_final_rejection_reason": rejection_reason,
            "llm_role_reply_retry_used": retry_used,
            "llm_role_reply_retry_accepted": retry_accepted,
            "llm_role_reply_fallback_used": fallback_used,
            "llm_role_reply_normalized_terms": sorted(set(normalized_terms)),
        }
    else:
        state.draft_reply = result.reply_text
        if (
            direct_presence_question_kind is not None
            and deps.companion.llm_provider_name != "fake"
        ):
            direct_reply_accepted = presence_reply_matches(
                result.reply_text,
                direct_presence_question_kind,
            )
            retry_used = False
            retry_accepted = False
            if not direct_reply_accepted:
                retry_used = True
                rejection_reason = "direct_presence_question_not_answered"
                result = deps.companion.respond(
                    message=state.user_input,
                    mode=state.mode,
                    companion_display_name=state.user_profile.companion_display_name,
                    memory_context=state.memory_context,
                    retrieval_context=state.retrieval_context,
                    role_style_context=_direct_presence_repair_context(
                        role_style_context,
                        rejection_reason,
                    ),
                    conversation_history=state.conversation_history,
                )
                retry_accepted = presence_reply_matches(
                    result.reply_text,
                    direct_presence_question_kind,
                )
                direct_reply_accepted = retry_accepted
                state.draft_reply = result.reply_text

            fallback_used = not direct_reply_accepted
            if fallback_used:
                state.draft_reply = _fallback_presence_text(
                    state,
                    direct_presence_question_kind,
                )
            role_reply_detail = {
                "llm_direct_reply_accepted": direct_reply_accepted,
                "llm_direct_reply_retry_used": retry_used,
                "llm_direct_reply_retry_accepted": retry_accepted,
                "llm_direct_reply_fallback_used": fallback_used,
            }

    if role_style_trace is None:
        role_style_trace = {}
    role_style_trace.update(role_reply_detail)
    _append_companion_trace(
        state,
        deps,
        result,
        extra_detail=role_style_trace or None,
    )
    return state


def _relationship_cue_context(
    decision,
    fallback_cue: str,
    *,
    topic_card_opening: bool = False,
    topic_card_refusal: bool = False,
) -> str:
    candidate_roles = (
        ", ".join(r.value for r in decision.candidate_roles) or "none"
    )
    selected_roles = ", ".join(r.value for r in decision.selected_roles) or "none"
    silent_roles = ", ".join(r.value for r in decision.silent_roles) or "none"
    cueing_style = (
        "boundary_acknowledgement"
        if topic_card_refusal
        else decision.cueing_style.value
    )
    context = (
        f"topic: {decision.topic}\n"
        f"candidate_relationship_functions: {candidate_roles}\n"
        f"selected_relationship_functions: {selected_roles}\n"
        f"silent_relationship_functions: {silent_roles}\n"
        f"cueing_style: {cueing_style}\n"
        f"allow_follow_up: {decision.allow_follow_up}\n"
        f"follow_up_reason: {decision.follow_up_reason}\n"
        f"role_selection_reason: {decision.role_selection_reason}\n"
        f"boundary_notes: {'; '.join(decision.boundary_notes)}\n"
        "offline_template_for_reference:\n"
        f"{fallback_cue}"
    )
    if topic_card_opening:
        context += (
            "\ninteraction_intent: acknowledge_user_then_open_topic\n"
            "这是话题卡开场。上面的 topic 是系统提供的背景，不是用户刚刚亲口说出的内容。"
            "必须先自然回应本轮真实用户消息；如果用户在打招呼，第一位角色要先回问候，"
            "本轮以回应问候为主；只有 allow_follow_up=true 时才可轻轻确认是否进入话题，"
            "不要让多个角色立即各自展开 topic。不得假装用户已经讲过相关经历。"
        )
    if topic_card_refusal:
        context += (
            "\ninteraction_intent: acknowledge_topic_refusal\n"
            "用户已拒绝当前话题。只需由本轮实际发言角色确认，必须立即停止旧话题；"
            "不得追问、不得邀请用户继续讲、不得自动指定新话题。"
        )
    return context


def relationship_cueing_node(state: GraphState, deps: GraphDeps) -> GraphState:
    """Stage 2–3 visible relationship roles into a short social cue (#53).

    Runs only for NON-SENSITIVE reminiscence turns (the Coordinator gate already
    excludes grief/health/privacy/loneliness). Reads memory context, asks the
    deterministic RelationshipOrchestratorAgent which visible roles speak, then
    builds a deterministic CueGenerator fallback, then lets CompanionAgent render
    the cue when a real provider is configured. Memory read/write is preserved
    around this node so preferences (e.g. 粤剧) still get saved.
    """

    role_selection_mode = state.role_selection_mode
    selected_role_ids = list(state.selected_role_ids or [])
    if state.study_condition == StudyCondition.c2_fixed_role_prelude:
        role_selection_mode = RoleSelectionMode.manual
        selected_role_ids = [RoleId.same_age_peer, RoleId.curious_junior]

    topic_card_start = _is_topic_card_start_turn(state)
    topic_card_refusal = _is_topic_card_refusal_turn(state)
    topic_card_greeting = topic_card_start and is_greeting_turn(state.user_input)
    visible_cueing_style = (
        "boundary_acknowledgement"
        if topic_card_refusal
        else None
    )
    relationship_input = _relationship_cue_input(state)
    inp = OrchestrationInput(
        user_input=relationship_input,
        memory_context=list(state.memory_context or []),
        recent_emotion_or_tone=None,
        user_role_preferences=None,
        role_selection_mode=role_selection_mode,
        selected_role_ids=selected_role_ids,
        risk_flags=None,
    )
    decision = deps.relationship_orchestrator.orchestrate(inp)
    fallback_cue = deps.cue_generator.generate(
        decision,
        state.user_input,
        topic_card_opening=topic_card_start,
        topic_card_refusal=topic_card_refusal,
    )
    state.memory_used = bool(state.memory_context)
    state.role_messages = role_messages_from_cue(
        fallback_cue,
        decision.selected_roles,
    )
    state.requested_relationship_roles = [r.value for r in selected_role_ids]
    state.relationship_role_selection_mode = role_selection_mode.value
    state.relationship_role_selection_source = decision.role_selection_source.value
    state.interaction_intent = decision.interaction_intent.value
    state.candidate_relationship_roles = [
        r.value for r in decision.candidate_roles if r is not RoleId.no_ai_role
    ]
    state.selected_relationship_roles = [
        r.value for r in decision.selected_roles if r is not RoleId.no_ai_role
    ]
    state.silent_relationship_roles = [
        r.value for r in decision.silent_roles if r is not RoleId.no_ai_role
    ]
    state.relationship_primary_role = (
        decision.primary_role.value
        if decision.primary_role and decision.primary_role is not RoleId.no_ai_role
        else None
    )
    state.relationship_topic = decision.topic
    state.relationship_boundary_notes = list(decision.boundary_notes)
    if topic_card_refusal:
        state.relationship_boundary_notes.insert(
            0,
            "用户拒绝当前话题：仅由本轮实际发言角色确认边界，并停止延续该话题。",
        )
    state.cueing_style = visible_cueing_style or decision.cueing_style.value
    state.relationship_allow_follow_up = decision.allow_follow_up
    state.relationship_follow_up_reason = decision.follow_up_reason
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.relationship_orchestrator.name,
            summary=(
                "用户拒绝当前话题；由实际发言角色确认并停止旧话题"
                if topic_card_refusal
                else decision.trace_visible_summary
            ),
            detail={
                "topic": decision.topic,
                "study_condition": state.study_condition.value,
                "study_session_id": state.study_session_id,
                "elder_control_action": state.elder_control_action.value,
                "role_selection_mode": role_selection_mode.value,
                "role_selection_source": decision.role_selection_source.value,
                "interaction_intent": decision.interaction_intent.value,
                "context_role_ids": [role_id.value for role_id in state.context_role_ids],
                "requested_role_ids": [r.value for r in selected_role_ids],
                "candidate_roles": [
                    r.value for r in decision.candidate_roles if r is not RoleId.no_ai_role
                ],
                "selected_roles": [
                    r.value for r in decision.selected_roles if r is not RoleId.no_ai_role
                ],
                "silent_roles": [
                    r.value for r in decision.silent_roles if r is not RoleId.no_ai_role
                ],
                "topic_id": state.topic_id,
                "topic_label": state.topic_label,
                "topic_card_opening": topic_card_start,
                "topic_card_greeting": topic_card_greeting,
                "topic_card_refusal": topic_card_refusal,
                "material_type": (
                    state.material_type.value if state.material_type else None
                ),
                "primary_role": (
                    decision.primary_role.value if decision.primary_role else None
                ),
                "cueing_style": state.cueing_style,
                "allow_follow_up": decision.allow_follow_up,
                "follow_up_reason": decision.follow_up_reason,
                "role_selection_reason": decision.role_selection_reason,
                "boundary_notes": state.relationship_boundary_notes,
                "role_trace": decision.role_trace,
                "topic_trace": decision.topic_trace,
                "memory_trace": decision.memory_trace,
                "boundary_trace": (
                    "用户明确拒绝当前话题；仅由实际发言角色确认边界后停止旧话题。"
                    if topic_card_refusal
                    else decision.boundary_trace
                ),
            },
        )
    )
    if deps.companion.llm_provider_name == "fake":
        state.draft_reply = fallback_cue
        return state

    state.conversation_history_used = bool(state.conversation_history)
    role_style_context = None
    selected_talk_roles = [
        role_id
        for role_id in decision.selected_roles
        if role_id is not RoleId.no_ai_role
    ]
    if selected_talk_roles:
        role_style_context = _role_style_context_for_profiles(
            [get_role_profile(role_id) for role_id in selected_talk_roles],
            (
                "系统保留这些关系角色来确认用户的当前话题边界"
                if topic_card_refusal
                else "系统本轮为话题引导分配了这些关系角色"
            ),
            topic_card_refusal=topic_card_refusal,
        )
    companion_message = state.user_input
    relationship_cue_context = _relationship_cue_context(
        decision,
        fallback_cue,
        topic_card_opening=topic_card_start,
        topic_card_refusal=topic_card_refusal,
    )
    result = deps.companion.respond(
        message=companion_message,
        mode=state.mode,
        companion_display_name=state.user_profile.companion_display_name,
        memory_context=state.memory_context,
        conversation_history=state.conversation_history,
        relationship_cue_context=relationship_cue_context,
        role_style_context=role_style_context,
    )
    (
        prepared_reply_text,
        real_role_messages,
        role_reply_accepted,
        role_reply_rejection_reason,
        normalized_terms,
    ) = _prepare_role_reply(
        result.reply_text,
        selected_talk_roles,
        topic_card_refusal=topic_card_refusal,
        require_greeting_acknowledgement=topic_card_greeting,
    )
    initial_rejection_reason = role_reply_rejection_reason
    retry_used = False
    retry_accepted = False

    if not role_reply_accepted and selected_talk_roles:
        retry_used = True
        result = deps.companion.respond(
            message=companion_message,
            mode=state.mode,
            companion_display_name=state.user_profile.companion_display_name,
            memory_context=state.memory_context,
            conversation_history=state.conversation_history,
            relationship_cue_context=relationship_cue_context,
            role_style_context=_role_reply_repair_context(
                role_style_context,
                selected_talk_roles,
                role_reply_rejection_reason,
            ),
        )
        (
            prepared_reply_text,
            real_role_messages,
            role_reply_accepted,
            role_reply_rejection_reason,
            retry_normalized_terms,
        ) = _prepare_role_reply(
            result.reply_text,
            selected_talk_roles,
            topic_card_refusal=topic_card_refusal,
            require_greeting_acknowledgement=topic_card_greeting,
        )
        normalized_terms.extend(retry_normalized_terms)
        retry_accepted = role_reply_accepted

    fallback_used = not role_reply_accepted
    if role_reply_accepted:
        state.draft_reply = prepared_reply_text
        state.role_messages = real_role_messages
    else:
        state.draft_reply = fallback_cue
        state.role_messages = role_messages_from_cue(
            fallback_cue,
            decision.selected_roles,
        )
    _append_companion_trace(
        state,
        deps,
        result,
        extra_detail={
            "relationship_cueing": True,
            "companion_input_source": "raw_user_input",
            "topic_card_greeting": topic_card_greeting,
            "topic_card_refusal": topic_card_refusal,
            "relationship_cue_fallback_template": fallback_cue,
            "manual_role_style": role_selection_mode is RoleSelectionMode.manual,
            "auto_role_style": role_selection_mode is RoleSelectionMode.auto,
            "manual_no_ai_role": RoleId.no_ai_role in selected_role_ids,
            "selected_roles": [role_id.value for role_id in selected_talk_roles],
            "role_labels": [
                get_role_profile(role_id).label_zh for role_id in selected_talk_roles
            ],
            "llm_role_reply_accepted": role_reply_accepted,
            "llm_role_reply_initial_rejection_reason": initial_rejection_reason,
            "llm_role_reply_final_rejection_reason": role_reply_rejection_reason,
            "llm_role_reply_retry_used": retry_used,
            "llm_role_reply_retry_accepted": retry_accepted,
            "llm_role_reply_fallback_used": fallback_used,
            "llm_role_reply_rejection_reason": role_reply_rejection_reason,
            "llm_role_reply_normalized_terms": sorted(set(normalized_terms)),
        },
    )
    return state


def safety_node(state: GraphState, deps: GraphDeps) -> GraphState:
    result = deps.safety_critic.review(state.risk)
    state.draft_reply = result.response_text
    state.safety_critic_used = True
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.safety_critic.name,
            summary=result.trace_summary(),
            detail={
                "template": result.template,
                "category": result.category,
                "risk_level": result.level.value,
            },
        )
    )
    return state


def proactive_node(state: GraphState, deps: GraphDeps) -> GraphState:
    # Dormant in Slice 3: GuardianAgent (#12) consuming StateEvent (#22) fills
    # this in. Kept so the proactive route is complete and testable.
    state.draft_reply = "如果现在方便，我可以陪您聊两句。"
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name="CoordinatorAgent",
            summary="proactive_checkin 路由（GuardianAgent 将在 #12/#22 接入）",
            detail={"placeholder": True},
        )
    )
    return state


def memory_write_node(state: GraphState, deps: GraphDeps) -> GraphState:
    if state.memory_scope == "session_only":
        state.tools.append(
            TraceStep(
                kind=TraceEntryKind.memory,
                name=deps.memory_triage_policy.name,
                summary="当前窗口使用独立上下文，未写入长期记忆",
                detail={"memory_scope": state.memory_scope},
            )
        )
        return state

    # Respect the profile master switch (#21) in addition to the Memory Center
    # pause (checked below before candidate extraction).
    if not state.user_profile.memory_enabled:
        return state

    if deps.memory_tool.is_extraction_paused(state.user_id):
        state.tools.append(
            TraceStep(
                kind=TraceEntryKind.memory,
                name=deps.memory_triage_policy.name,
                summary="记忆提取已暂停，未抽取候选或写入",
                detail={"extraction_paused": True},
            )
        )
        return state

    candidate = deps.memory_candidate_extractor.extract_one(
        state.user_input, state.turn_id
    )
    if candidate is None:
        return state

    existing_memories = deps.memory_tool.load_context(state.user_id)
    existing_cards = deps.memory_card_store.list(state.user_id)
    decision = deps.memory_triage_policy.decide(
        candidate,
        existing_memories=existing_memories,
        existing_cards=existing_cards,
    )

    saved_memory_id: str | None = None
    card_id: str | None = None
    updated_memory_id: str | None = None
    if decision.action == MemoryTriageAction.auto_save:
        saved = deps.memory_tool.save_candidate(state.user_id, candidate)
        if saved is not None:
            saved_memory_id = saved.id
    elif decision.action in {
        MemoryTriageAction.create_card,
        MemoryTriageAction.create_boundary_card,
    }:
        card = deps.memory_card_tool.draft_from_candidate(state.user_id, candidate)
        deps.memory_card_store.add(card)
        card_id = card.card_id
    elif (
        decision.action == MemoryTriageAction.update_existing
        and decision.target_memory_id is not None
    ):
        updated = deps.memory_tool.update_candidate(
            state.user_id, decision.target_memory_id, candidate
        )
        if updated is not None:
            updated_memory_id = updated.id

    state.tools.append(
        TraceStep(
            kind=TraceEntryKind.memory,
            name=deps.memory_triage_policy.name,
            summary=(
                f"{candidate.candidate_type.value} → {decision.action.value}："
                f"{decision.reason}"
            ),
            detail={
                "candidate_type": candidate.candidate_type.value,
                "decision": decision.model_dump(mode="json"),
                "saved": saved_memory_id is not None,
                "saved_memory_id": saved_memory_id,
                "memory_card_id": card_id,
                "updated_memory_id": updated_memory_id,
            },
        )
    )
    return state


def reminder_node(state: GraphState, deps: GraphDeps) -> GraphState:
    reminder = deps.reminder_tool.create_from_text(state.user_id, state.user_input)
    if reminder is None:
        state.draft_reply = (
            "您是想让我几点提醒您做什么呢？比如可以说「每天早上八点提醒我吃药」。"
        )
        state.tools.append(
            TraceStep(
                kind=TraceEntryKind.tool,
                name=deps.reminder_tool.name,
                summary="未解析出时间，已请用户补充",
                detail={"created": False},
            )
        )
        return state

    state.draft_reply = deps.reminder_tool.confirm_phrase(reminder)
    state.tools.append(
        TraceStep(
            kind=TraceEntryKind.tool,
            name=deps.reminder_tool.name,
            summary=(
                f"已创建提醒：{reminder.recurrence.value} {reminder.time} "
                f"{reminder.content}"
            ),
            detail={
                "created": True,
                "reminder_id": reminder.id,
                "time": reminder.time,
                "recurrence": reminder.recurrence.value,
                "content": reminder.content,
            },
        )
    )
    return state


def output_guard_node(state: GraphState, deps: GraphDeps) -> GraphState:
    result = deps.output_guard.run(state.draft_reply)
    state.response_text = result.final_text
    state.guards.append(
        TraceStep(
            kind=TraceEntryKind.guard,
            name=deps.output_guard.name,
            summary=result.summary,
            detail={"rewritten": result.rewritten},
        )
    )
    return state
