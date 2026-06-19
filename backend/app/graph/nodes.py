"""Graph nodes (issue #5).

Each node takes the shared ``GraphState`` and the ``GraphDeps`` (agent / guard
instances) and mutates the state, appending trace steps tagged by kind so the
Agent / Tool / Guard distinction stays visible.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.agents.companion import CompanionAgent
from app.agents.coordinator import CoordinatorAgent
from app.agents.safety_critic import SafetyCriticAgent
from app.core.constants import TraceEntryKind
from app.graph.state import GraphState
from app.schemas.trace import TraceStep
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


def companion_node(state: GraphState, deps: GraphDeps) -> GraphState:
    result = deps.companion.respond(
        message=state.user_input,
        mode=state.mode,
        companion_display_name=state.user_profile.companion_display_name,
        memory_context=state.memory_context,
    )
    state.draft_reply = result.reply_text
    state.agents.append(
        TraceStep(
            kind=TraceEntryKind.agent,
            name=deps.companion.name,
            summary=result.trace_summary(),
            detail={
                "mode": result.mode.value,
                "companion_display_name": result.companion_display_name,
                "named_by_user": result.named_by_user,
                "prompt_version": deps.companion.prompt_version,
            },
        )
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
