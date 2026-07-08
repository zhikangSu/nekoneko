"""Graph assembly + runner (issues #5, #10, #11).

A framework-free sequential runner with conditional branching. Structured like a
LangGraph build so it can be swapped for real LangGraph later:

    input_guard → coordinator → response_pipeline(route) → output_guard

where the companion pipeline is memory_read → companion → memory_write.
"""

from __future__ import annotations

from app.agents.companion import CompanionAgent
from app.agents.coordinator import CoordinatorAgent
from app.agents.relationship_orchestrator import RelationshipOrchestratorAgent
from app.agents.safety_critic import SafetyCriticAgent
from app.core.config import Settings
from app.relationship.cue_generator import CueGenerator
from app.graph.edges import response_pipeline
from app.graph.nodes import (
    GraphDeps,
    coordinator_node,
    input_guard_node,
    output_guard_node,
)
from app.graph.state import GraphState
from app.services.llm_provider import get_llm_provider
from app.stores.memory_card_store import MemoryCardStore
from app.stores.memory_store import MemoryStore
from app.stores.reminder_store import ReminderStore
from app.tools.info_retrieval import InfoRetrievalTool
from app.tools.input_rule_guard import InputRuleGuard
from app.tools.memory_card_tool import MemoryCardTool
from app.tools.memory_candidate_extractor import MemoryCandidateExtractor
from app.tools.memory_triage_policy import MemoryTriagePolicy
from app.tools.memory_tool import MemoryTool
from app.tools.output_rule_guard import OutputRuleGuard
from app.tools.reminder_tool import ReminderTool


def build_deps(settings: Settings) -> GraphDeps:
    memory_store = MemoryStore(settings.resolved_memory_root)
    return GraphDeps(
        input_guard=InputRuleGuard(),
        output_guard=OutputRuleGuard(),
        coordinator=CoordinatorAgent(),
        companion=CompanionAgent(get_llm_provider(settings)),
        safety_critic=SafetyCriticAgent(),
        memory_tool=MemoryTool(memory_store),
        memory_card_tool=MemoryCardTool(memory_store),
        memory_card_store=MemoryCardStore(settings.resolved_memory_cards_dir),
        memory_candidate_extractor=MemoryCandidateExtractor(),
        memory_triage_policy=MemoryTriagePolicy(),
        reminder_tool=ReminderTool(ReminderStore(settings.resolved_reminder_dir)),
        info_retrieval=InfoRetrievalTool(
            settings.retrieval_provider,
            demo_mode=settings.demo_mode,
            lat=settings.retrieval_lat,
            lon=settings.retrieval_lon,
            location=settings.retrieval_location,
            timeout=settings.retrieval_timeout_seconds,
        ),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )


def run_turn(state: GraphState, deps: GraphDeps) -> GraphState:
    input_guard_node(state, deps)
    coordinator_node(state, deps)
    for node in response_pipeline(state.route):
        node(state, deps)
    output_guard_node(state, deps)
    return state
