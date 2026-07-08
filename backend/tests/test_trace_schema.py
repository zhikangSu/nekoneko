from app.core.constants import CompanionMode, RiskLevel, Route, TraceEntryKind
from app.schemas.trace import AgentTrace, TraceStep


def test_agent_trace_minimal_valid():
    trace = AgentTrace(
        turn_id="t_test",
        mode=CompanionMode.role_first,
        route=Route.companion_chat,
        risk_level=RiskLevel.low,
    )
    assert trace.agents == []
    assert trace.tools == []
    assert trace.guards == []
    assert trace.state_event is None
    assert trace.retrieval_used is False

    dumped = trace.model_dump(mode="json")
    for key in (
        "turn_id",
        "mode",
        "route",
        "risk_level",
        "agents",
        "tools",
        "guards",
        "state_event",
        "memory_used",
        "retrieval_used",
        "safety_critic_used",
        "research_metadata",
        "research_trace",
    ):
        assert key in dumped
    assert dumped["research_trace"]["boundary"]["boundary_state"] == "none"


def test_trace_step_keeps_kind_distinction():
    agent = TraceStep(kind=TraceEntryKind.agent, name="CompanionAgent")
    tool = TraceStep(kind=TraceEntryKind.tool, name="MemoryTool", summary="read")
    guard = TraceStep(kind=TraceEntryKind.guard, name="InputRuleGuard")
    assert agent.kind == "agent"
    assert tool.kind == "tool"
    assert guard.kind == "guard"
    assert tool.summary == "read"
