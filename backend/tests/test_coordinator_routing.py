from app.agents.coordinator import CoordinatorAgent
from app.core.config import Settings
from app.core.constants import CompanionMode, Route
from app.graph.build_graph import build_deps, run_turn
from app.graph.state import GraphState
from app.safety.risk_classifier import classify_risk
from app.schemas.profile import UserProfile


def _decide(message: str, has_state_event: bool = False):
    return CoordinatorAgent().decide(
        classification=classify_risk(message),
        has_state_event=has_state_event,
    )


def test_low_risk_routes_to_companion():
    assert _decide("你好，今天过得怎么样").route == Route.companion_chat


def test_medical_symptom_routes_to_safety():
    assert _decide("我胸口痛").route == Route.safety_response


def test_fall_routes_to_emergency_mock():
    assert _decide("我摔倒了起不来").route == Route.emergency_mock


def test_emotional_crisis_routes_to_safety_not_emergency():
    assert _decide("我不想活了").route == Route.safety_response


def test_state_event_routes_to_proactive_when_low_risk():
    assert _decide("（系统触发）", has_state_event=True).route == Route.proactive_checkin


def test_risk_takes_priority_over_state_event():
    decision = _decide("我胸口痛", has_state_event=True)
    assert decision.route == Route.safety_response


def _state(message: str, **kwargs) -> GraphState:
    return GraphState(
        turn_id="t_test",
        user_id="demo_user",
        user_input=message,
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="demo_user"),
        **kwargs,
    )


def test_graph_low_risk_produces_companion_and_guards():
    deps = build_deps(Settings())
    state = run_turn(_state("今天想喝点茶"), deps)
    assert state.route == Route.companion_chat
    assert state.safety_critic_used is False
    assert state.response_text.strip()
    guard_names = [g.name for g in state.guards]
    assert "InputRuleGuard" in guard_names and "OutputRuleGuard" in guard_names
    agent_names = [a.name for a in state.agents]
    assert "CoordinatorAgent" in agent_names and "CompanionAgent" in agent_names


def test_graph_proactive_route_runs_without_companion():
    deps = build_deps(Settings())
    state = run_turn(_state("（系统触发）", state_event={"type": "poor_sleep"}), deps)
    assert state.route == Route.proactive_checkin
    assert state.response_text.strip()
    assert "CompanionAgent" not in [a.name for a in state.agents]
