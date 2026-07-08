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
    is_relationship_cue_turn,
    role_messages_from_cue,
)
from app.schemas.relationship import (
    ElderControlAction,
    OrchestrationInput,
    RoleId,
    RoleSelectionMode,
    StudyCondition,
)
from app.schemas.trace import TraceStep
from app.tools.info_retrieval import InfoRetrievalTool
from app.tools.input_rule_guard import InputRuleGuard
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
    reminder_tool: ReminderTool
    info_retrieval: InfoRetrievalTool
    relationship_orchestrator: RelationshipOrchestratorAgent
    cue_generator: CueGenerator


_TOPIC_CARD_CUE_TEXT: dict[str, str] = {
    "T01": "年轻的时候读书上学",
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
    "继续",
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
    return any(marker in text for marker in _GENERIC_TOPIC_CARD_MARKERS)


def _relationship_cue_input(state: GraphState) -> str:
    if is_relationship_cue_turn(state.user_input):
        return state.user_input
    seed = _topic_card_seed_text(state)
    if seed and _can_topic_card_seed_cue(state):
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
    if is_relationship_cue_turn(state.user_input):
        return True
    seed = _topic_card_seed_text(state)
    return bool(
        seed and _can_topic_card_seed_cue(state) and is_relationship_cue_turn(seed)
    )


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
    }
    if extra_detail:
        detail.update(extra_detail)
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.companion.name,
            summary=result.trace_summary(),
            detail=detail,
        )
    )


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
    result = deps.companion.respond(
        message=state.user_input,
        mode=state.mode,
        companion_display_name=state.user_profile.companion_display_name,
        memory_context=state.memory_context,
        retrieval_context=state.retrieval_context,
    )
    state.draft_reply = result.reply_text
    _append_companion_trace(state, deps, result)
    return state


def _relationship_cue_context(decision, fallback_cue: str) -> str:
    selected_roles = ", ".join(r.value for r in decision.selected_roles) or "none"
    return (
        f"topic: {decision.topic}\n"
        f"selected_relationship_functions: {selected_roles}\n"
        f"cueing_style: {decision.cueing_style.value}\n"
        f"role_selection_reason: {decision.role_selection_reason}\n"
        f"boundary_notes: {'; '.join(decision.boundary_notes)}\n"
        "offline_template_for_reference:\n"
        f"{fallback_cue}"
    )


def relationship_cueing_node(state: GraphState, deps: GraphDeps) -> GraphState:
    """Stage 2–3 visible relationship roles into a short social cue (#53).

    Runs only for NON-SENSITIVE reminiscence turns (the Coordinator gate already
    excludes grief/health/privacy/loneliness). Reads memory context, asks the
    deterministic RelationshipOrchestratorAgent which visible roles speak, then
    renders the cue with CueGenerator. Memory read/write is preserved around this
    node so preferences (e.g. 粤剧) still get saved.
    """

    role_selection_mode = state.role_selection_mode
    selected_role_ids = list(state.selected_role_ids or [])
    if state.study_condition == StudyCondition.c2_fixed_role_prelude:
        role_selection_mode = RoleSelectionMode.manual
        selected_role_ids = [RoleId.same_age_peer, RoleId.curious_junior]

    inp = OrchestrationInput(
        user_input=_relationship_cue_input(state),
        memory_context=list(state.memory_context or []),
        recent_emotion_or_tone=None,
        user_role_preferences=None,
        role_selection_mode=role_selection_mode,
        selected_role_ids=selected_role_ids,
        risk_flags=None,
    )
    decision = deps.relationship_orchestrator.orchestrate(inp)
    fallback_cue = deps.cue_generator.generate(decision, state.user_input)
    state.memory_used = bool(state.memory_context)
    state.role_messages = role_messages_from_cue(
        fallback_cue,
        decision.selected_roles,
    )
    state.selected_relationship_roles = [r.value for r in decision.selected_roles]
    state.cueing_style = decision.cueing_style.value
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.relationship_orchestrator.name,
            summary=decision.trace_visible_summary,
            detail={
                "topic": decision.topic,
                "study_condition": state.study_condition.value,
                "study_session_id": state.study_session_id,
                "elder_control_action": state.elder_control_action.value,
                "role_selection_mode": role_selection_mode.value,
                "requested_role_ids": [r.value for r in selected_role_ids],
                "selected_roles": [r.value for r in decision.selected_roles],
                "topic_id": state.topic_id,
                "topic_label": state.topic_label,
                "material_type": (
                    state.material_type.value if state.material_type else None
                ),
                "primary_role": (
                    decision.primary_role.value if decision.primary_role else None
                ),
                "cueing_style": decision.cueing_style.value,
                "role_selection_reason": decision.role_selection_reason,
                "boundary_notes": decision.boundary_notes,
                "role_trace": decision.role_trace,
                "topic_trace": decision.topic_trace,
                "memory_trace": decision.memory_trace,
                "boundary_trace": decision.boundary_trace,
            },
        )
    )
    if deps.companion.llm_provider_name == "fake":
        state.draft_reply = fallback_cue
        return state

    result = deps.companion.respond(
        message=state.user_input,
        mode=state.mode,
        companion_display_name=state.user_profile.companion_display_name,
        memory_context=state.memory_context,
        relationship_cue_context=_relationship_cue_context(decision, fallback_cue),
    )
    state.draft_reply = result.reply_text
    _append_companion_trace(
        state,
        deps,
        result,
        extra_detail={
            "relationship_cueing": True,
            "relationship_cue_fallback_template": fallback_cue,
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
    # Respect the profile master switch (#21) in addition to the Memory Center
    # pause (checked inside remember_from_text).
    if not state.user_profile.memory_enabled:
        return state
    saved = deps.memory_tool.remember_from_text(state.user_id, state.user_input)
    if saved:
        contents = [e.content for e in saved]
        state.tools.append(
            TraceStep(
                kind=TraceEntryKind.memory,
                name=deps.memory_tool.name,
                summary=f"提取并记住 {len(saved)} 条偏好：{'、'.join(contents)}",
                detail={"saved": contents},
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
