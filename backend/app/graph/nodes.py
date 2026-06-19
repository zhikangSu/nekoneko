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
from app.tools.output_rule_guard import OutputRuleGuard


@dataclass
class GraphDeps:
    input_guard: InputRuleGuard
    output_guard: OutputRuleGuard
    coordinator: CoordinatorAgent
    companion: CompanionAgent
    safety_critic: SafetyCriticAgent


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


def companion_node(state: GraphState, deps: GraphDeps) -> GraphState:
    result = deps.companion.respond(
        message=state.user_input,
        mode=state.mode,
        companion_display_name=state.user_profile.companion_display_name,
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
