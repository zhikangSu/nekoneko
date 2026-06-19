"""Graph assembly + runner (issue #5).

A framework-free sequential runner with one conditional branch. Structured like
a LangGraph build so it can be swapped for real LangGraph later:

    input_guard → coordinator → (companion | safety | proactive) → output_guard
"""

from __future__ import annotations

from app.agents.companion import CompanionAgent
from app.agents.coordinator import CoordinatorAgent
from app.agents.safety_critic import SafetyCriticAgent
from app.core.config import Settings
from app.graph.edges import select_response_node
from app.graph.nodes import (
    GraphDeps,
    coordinator_node,
    input_guard_node,
    output_guard_node,
)
from app.graph.state import GraphState
from app.services.llm_provider import get_llm_provider
from app.tools.input_rule_guard import InputRuleGuard
from app.tools.output_rule_guard import OutputRuleGuard


def build_deps(settings: Settings) -> GraphDeps:
    return GraphDeps(
        input_guard=InputRuleGuard(),
        output_guard=OutputRuleGuard(),
        coordinator=CoordinatorAgent(),
        companion=CompanionAgent(get_llm_provider(settings)),
        safety_critic=SafetyCriticAgent(),
    )


def run_turn(state: GraphState, deps: GraphDeps) -> GraphState:
    input_guard_node(state, deps)
    coordinator_node(state, deps)
    select_response_node(state.route)(state, deps)
    output_guard_node(state, deps)
    return state
