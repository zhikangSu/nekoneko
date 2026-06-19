import pytest

from app.core.constants import CompanionMode, RiskLevel, Route
from app.schemas.trace import AgentTrace, TraceRecord
from app.stores.trace_store import TraceStore


def _record(turn_id: str, user_id: str, created_at: str, route=Route.companion_chat) -> TraceRecord:
    return TraceRecord(
        turn_id=turn_id,
        user_id=user_id,
        created_at=created_at,
        trace=AgentTrace(
            turn_id=turn_id,
            mode=CompanionMode.role_first,
            route=route,
            risk_level=RiskLevel.low,
        ),
    )


def test_save_and_get_roundtrip(tmp_path):
    store = TraceStore(tmp_path)
    store.save(_record("t_a", "demo_user", "2026-06-19T10:00:00+00:00"))
    got = store.get("t_a")
    assert got is not None
    assert got.turn_id == "t_a"
    assert got.trace.route == Route.companion_chat


def test_get_missing_returns_none(tmp_path):
    assert TraceStore(tmp_path).get("t_missing") is None


def test_list_filters_by_user_and_sorts_desc(tmp_path):
    store = TraceStore(tmp_path)
    store.save(_record("t_1", "demo_user", "2026-06-19T10:00:00+00:00"))
    store.save(_record("t_2", "demo_user", "2026-06-19T12:00:00+00:00"))
    store.save(_record("t_3", "other_user", "2026-06-19T11:00:00+00:00"))

    summaries = store.list(user_id="demo_user")
    assert [s.turn_id for s in summaries] == ["t_2", "t_1"]  # newest first
    assert all(s.user_id == "demo_user" for s in summaries)


def test_list_respects_limit(tmp_path):
    store = TraceStore(tmp_path)
    for i in range(5):
        store.save(_record(f"t_{i}", "demo_user", f"2026-06-19T10:0{i}:00+00:00"))
    assert len(store.list(user_id="demo_user", limit=3)) == 3


def test_invalid_turn_id_raises(tmp_path):
    with pytest.raises(ValueError):
        TraceStore(tmp_path).get("../etc")
