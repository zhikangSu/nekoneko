"""Tests for the relationship_cueing route (issue #53).

Covers the new NON-SENSITIVE reminiscence cueing path end-to-end via the chat
client, plus regression guards proving sensitive / loneliness / off-topic turns
stay on the existing companion path. Uses fake/mock providers only (conftest).
"""

from __future__ import annotations

from app.relationship.cue_generator import CueGenerator, is_relationship_cue_turn
from app.relationship.role_profiles import MAX_ROLES_PER_TURN, list_role_profiles
from app.schemas.relationship import OrchestrationInput
from app.agents.relationship_orchestrator import RelationshipOrchestratorAgent


# Chinese labels for the visible roles, so tests can count role lines and assert
# distinct labels without hardcoding role internals.
_ROLE_LABELS = [p.label_zh for p in list_role_profiles()]


def _route(body: dict) -> str:
    return body["agent_trace"]["route"]


def _role_lines(text: str) -> list[str]:
    """Lines that start with a visible-role label + '：' (one per role)."""

    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if any(line.startswith(f"{label}：") for label in _ROLE_LABELS):
            lines.append(line)
    return lines


def _distinct_role_labels(text: str) -> set[str]:
    return {label for label in _ROLE_LABELS if f"{label}：" in text}


# ---------------------------------------------------------------------------
# Scenario 1: old TV / old object -> multi-role cue
# ---------------------------------------------------------------------------


def test_old_tv_routes_to_relationship_cueing_with_multi_role_cue(client):
    body = client.post(
        "/api/chat",
        json={"user_id": "cue_tv", "message": "看到这个老电视，我想起以前的日子"},
    ).json()

    assert _route(body) == "relationship_cueing"

    text = body["response_text"]
    # At least two distinct visible role labels appear.
    assert len(_distinct_role_labels(text)) >= 2
    # And a gentle, non-forcing invitation is present.
    assert any(kw in text for kw in ("想聊", "愿意", "不想说也没关系", "不着急"))

    # Trace has an agent step from RelationshipOrchestratorAgent with a
    # non-empty role_trace, and its selected roles include same_age_peer.
    agents = body["agent_trace"]["agents"]
    orch = [a for a in agents if a["name"] == "RelationshipOrchestratorAgent"]
    assert len(orch) == 1
    assert orch[0]["kind"] == "agent"
    assert orch[0]["detail"]["role_trace"].strip()
    assert "same_age_peer" in orch[0]["detail"]["selected_roles"]


# ---------------------------------------------------------------------------
# Scenario 2: culture/arts preference -> cue route AND memory still saved
# ---------------------------------------------------------------------------


def test_yueju_routes_to_cue_and_saves_memory(client):
    uid = "cue_yueju"
    body = client.post(
        "/api/chat", json={"user_id": uid, "message": "我喜欢听粤剧"}
    ).json()

    assert _route(body) == "relationship_cueing"

    # Preference saved this turn (memory trace) ...
    tools = body["agent_trace"]["tools"]
    saved_blobs = [t["detail"].get("saved") for t in tools if t["detail"].get("saved")]
    assert any(any("粤剧" in item for item in blob) for blob in saved_blobs)

    # ... and readable back via the memory API.
    stored = client.get(f"/api/memory/{uid}").json()
    assert any("粤剧" in m["content"] for m in stored["memories"])


# ---------------------------------------------------------------------------
# Regression guards: non-cue topics stay on the companion path
# ---------------------------------------------------------------------------


def test_walking_stays_companion(client):
    body = client.post(
        "/api/chat", json={"user_id": "cue_walk", "message": "我喜欢散步"}
    ).json()
    assert _route(body) == "companion_chat"


def test_loneliness_stays_companion(client):
    body = client.post(
        "/api/chat", json={"user_id": "cue_lonely", "message": "我今天有点孤单"}
    ).json()
    assert _route(body) == "companion_chat"


def test_grief_missing_spouse_stays_companion(client):
    # REGRESSION GUARD: "老伴" is deceased_grief; it must NOT be cued.
    body = client.post(
        "/api/chat", json={"user_id": "cue_grief1", "message": "我今天有点想老伴了"}
    ).json()
    assert _route(body) == "companion_chat"


def test_deceased_spouse_not_cued_and_no_multi_role_banter(client):
    body = client.post(
        "/api/chat", json={"user_id": "cue_grief2", "message": "我想起已经离开的老伴"}
    ).json()
    assert _route(body) != "relationship_cueing"
    # No multi-role cue banter in a grief reply.
    assert len(_role_lines(body["response_text"])) == 0


# ---------------------------------------------------------------------------
# Cap: never more than MAX_ROLES_PER_TURN role lines
# ---------------------------------------------------------------------------


def test_cue_never_exceeds_max_role_lines(client):
    for message in (
        "看到这个老电视，我想起以前的日子",
        "我喜欢听粤剧",
        "以前在厂里上班的日子真怀念",
        "想起以前带孩子读书的事",
    ):
        body = client.post(
            "/api/chat", json={"user_id": "cue_cap", "message": message}
        ).json()
        if _route(body) == "relationship_cueing":
            assert len(_role_lines(body["response_text"])) <= MAX_ROLES_PER_TURN


# ---------------------------------------------------------------------------
# Unit-level checks on the classifier and generator
# ---------------------------------------------------------------------------


def test_is_relationship_cue_turn_excludes_sensitive_and_mood():
    assert is_relationship_cue_turn("看到这个老电视，我想起以前的日子") is True
    assert is_relationship_cue_turn("我喜欢听粤剧") is True
    assert is_relationship_cue_turn("我喜欢散步") is False
    assert is_relationship_cue_turn("我今天有点孤单") is False
    assert is_relationship_cue_turn("我今天有点想老伴了") is False
    assert is_relationship_cue_turn("我想起已经离开的老伴") is False


def test_generator_output_has_no_dependency_language():
    orch = RelationshipOrchestratorAgent()
    gen = CueGenerator()
    text = gen.generate(
        orch.orchestrate(OrchestrationInput(user_input="看到这个老电视，我想起以前的日子")),
        "看到这个老电视，我想起以前的日子",
    )
    for banned in ("只有我", "别结束", "再聊一会儿", "不用找别人"):
        assert banned not in text
