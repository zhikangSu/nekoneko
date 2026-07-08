"""Tests for the relationship_cueing route (issue #53).

Covers the new NON-SENSITIVE reminiscence cueing path end-to-end via the chat
client, plus regression guards proving sensitive / loneliness / off-topic turns
stay on the existing companion path. Uses fake/mock providers only (conftest).
"""

from __future__ import annotations

from types import SimpleNamespace

from app.agents.companion import CompanionAgent
from app.agents.relationship_orchestrator import RelationshipOrchestratorAgent
from app.core.constants import CompanionMode
from app.graph.nodes import relationship_cueing_node
from app.graph.state import GraphState
from app.relationship.cue_generator import CueGenerator, is_relationship_cue_turn
from app.relationship.role_profiles import MAX_ROLES_PER_TURN, list_role_profiles
from app.schemas.profile import UserProfile
from app.schemas.relationship import OrchestrationInput
from app.services.llm_provider import CompanionReplyInput, LLMProvider


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


def test_manual_roles_are_sent_to_orchestrator_trace(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_manual_roles",
            "message": "看到这个老电视，我想起以前的日子",
            "role_selection_mode": "manual",
            "selected_role_ids": ["same_age_peer", "curious_junior"],
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    orch = [
        a
        for a in body["agent_trace"]["agents"]
        if a["name"] == "RelationshipOrchestratorAgent"
    ]
    assert orch[0]["detail"]["role_selection_mode"] == "manual"
    assert orch[0]["detail"]["requested_role_ids"] == [
        "same_age_peer",
        "curious_junior",
    ]
    assert orch[0]["detail"]["selected_roles"] == [
        "same_age_peer",
        "curious_junior",
    ]
    assert "同龄共鸣者：" in body["response_text"]
    assert "晚辈好奇者：" in body["response_text"]


def test_manual_no_ai_role_suppresses_role_lines(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_manual_no_ai",
            "message": "看到这个老电视，我想起以前的日子",
            "role_selection_mode": "manual",
            "selected_role_ids": ["same_age_peer", "no_ai_role"],
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    assert _role_lines(body["response_text"]) == []
    assert "不安排 AI 角色" in body["response_text"]

    orch = [
        a
        for a in body["agent_trace"]["agents"]
        if a["name"] == "RelationshipOrchestratorAgent"
    ]
    assert orch[0]["detail"]["selected_roles"] == ["no_ai_role"]
    assert orch[0]["detail"]["cueing_style"] == "no_cue"


def test_topic_card_metadata_routes_generic_cue_and_returns_role_messages(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card",
            "message": "聊这个吧",
            "topic_id": "T05",
            "topic_label": "老照片或旧物件",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    assert len(body["role_messages"]) >= 2
    assert body["role_messages"][0]["role_label"]
    assert body["role_messages"][0]["text"]

    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["topic_id"] == "T05"
    assert metadata["material_type"] == "topic_card"
    assert "same_age_peer" in metadata["selected_roles"]
    assert metadata["cueing_style"] == "agent_agent_then_invite"


def test_study_condition_c1_disables_relationship_cueing_and_binds_session(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_condition_c1",
            "message": "看到这个老电视，我想起以前的日子",
            "study_condition": "c1_direct_question",
            "study_session_id": "session_c1",
        },
    ).json()

    assert _route(body) == "companion_chat"
    assert body["role_messages"] == []
    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["study_condition"] == "c1_direct_question"
    assert metadata["study_session_id"] == "session_c1"


def test_study_condition_c2_uses_fixed_role_prelude(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_condition_c2",
            "message": "聊这个吧",
            "topic_id": "T05",
            "topic_label": "老照片或旧物件",
            "material_type": "topic_card",
            "study_condition": "c2_fixed_role_prelude",
            "study_session_id": "session_c2",
            "role_selection_mode": "manual",
            "selected_role_ids": ["theme_companion"],
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["study_condition"] == "c2_fixed_role_prelude"
    assert metadata["study_session_id"] == "session_c2"
    assert metadata["selected_roles"] == ["same_age_peer", "curious_junior"]
    research_trace = body["agent_trace"]["research_trace"]
    assert research_trace["control"]["study_condition"] == "c2_fixed_role_prelude"
    assert research_trace["control"]["study_session_id"] == "session_c2"
    assert research_trace["topic"]["topic_id"] == "T05"
    assert research_trace["role"]["selected_roles"] == [
        "same_age_peer",
        "curious_junior",
    ]
    assert research_trace["role"]["role_selection_mode"] == "manual"

    orch = [
        a
        for a in body["agent_trace"]["agents"]
        if a["name"] == "RelationshipOrchestratorAgent"
    ]
    assert orch[0]["detail"]["role_selection_mode"] == "manual"
    assert orch[0]["detail"]["requested_role_ids"] == [
        "same_age_peer",
        "curious_junior",
    ]


def test_culture_topic_returns_two_role_lines_before_invitation(client):
    body = client.post(
        "/api/chat",
        json={"user_id": "cue_culture_scene", "message": "我喜欢听粤剧。"},
    ).json()

    assert _route(body) == "relationship_cueing"
    assert len(body["role_messages"]) >= 3
    first_two_labels = [m["role_label"] for m in body["role_messages"][:2]]
    assert first_two_labels == ["主题陪伴者", "同龄共鸣者"]
    assert body["role_messages"][2]["role_label"] == "晚辈好奇者"

    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["cueing_style"] == "agent_agent_then_invite"
    assert metadata["selected_roles"] == [
        "theme_companion",
        "same_age_peer",
        "curious_junior",
    ]


def test_elder_pause_roles_suppresses_relationship_cueing(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_control_pause",
            "message": "看到这个老电视，我想起以前的日子",
            "study_condition": "c3_relationship_aware",
            "study_session_id": "session_pause",
            "elder_control_action": "pause_roles",
        },
    ).json()

    assert _route(body) == "companion_chat"
    assert body["role_messages"] == []
    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["elder_control_action"] == "pause_roles"
    assert metadata["study_session_id"] == "session_pause"
    research_trace = body["agent_trace"]["research_trace"]
    assert research_trace["control"]["elder_control_action"] == "pause_roles"
    assert research_trace["boundary"]["boundary_state"] == "user_paused_roles"


def test_elder_continue_keeps_relationship_cueing(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_control_continue",
            "message": "看到这个老电视，我想起以前的日子",
            "study_condition": "c3_relationship_aware",
            "study_session_id": "session_continue",
            "elder_control_action": "continue_session",
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    assert len(body["role_messages"]) >= 2
    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["elder_control_action"] == "continue_session"
    assert metadata["study_session_id"] == "session_continue"


def test_elder_stop_reminiscence_suppresses_relationship_cueing(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_control_stop",
            "message": "看到这个老电视，我想起以前的日子",
            "elder_control_action": "stop_reminiscence",
        },
    ).json()

    assert _route(body) == "companion_chat"
    assert body["role_messages"] == []
    assert (
        body["agent_trace"]["research_metadata"]["elder_control_action"]
        == "stop_reminiscence"
    )


def test_topic_card_does_not_override_sensitive_user_input(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_sensitive",
            "message": "我今天有点想老伴了",
            "topic_id": "T05",
            "topic_label": "老照片或旧物件",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "companion_chat"
    assert body["role_messages"] == []
    assert body["agent_trace"]["research_metadata"]["topic_id"] == "T05"


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


def test_family_relationship_strain_stays_companion(client):
    body = client.post(
        "/api/chat",
        json={"user_id": "cue_family_strain", "message": "我孙子不想跟我讲话"},
    ).json()

    assert _route(body) == "companion_chat"
    assert len(_role_lines(body["response_text"])) == 0
    agent_names = [a["name"] for a in body["agent_trace"]["agents"]]
    assert "CompanionAgent" in agent_names
    assert "RelationshipOrchestratorAgent" not in agent_names


def test_grief_missing_spouse_stays_companion(client):
    # REGRESSION GUARD: "老伴" is deceased_grief; it must NOT be cued.
    body = client.post(
        "/api/chat", json={"user_id": "cue_grief1", "message": "我今天有点想老伴了"}
    ).json()
    assert _route(body) == "companion_chat"


def test_manual_roles_do_not_override_grief_boundary_route(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_manual_grief",
            "message": "我今天有点想老伴了",
            "role_selection_mode": "manual",
            "selected_role_ids": ["same_age_peer", "curious_junior"],
        },
    ).json()
    assert _route(body) == "companion_chat"
    assert len(_role_lines(body["response_text"])) == 0


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
    assert is_relationship_cue_turn("我孙子不想跟我讲话") is False
    assert is_relationship_cue_turn("儿子最近都不回我消息") is False
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


class _SpyRealLLMProvider(LLMProvider):
    name = "xiaomimimo"

    def __init__(self) -> None:
        self.payloads: list[CompanionReplyInput] = []

    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        self.payloads.append(payload)
        return "这些粤剧老段子听起来很有味道。您最喜欢的是哪一段呀？"

    @property
    def generation_info(self) -> dict:
        return {"provider": self.name, "model": "test", "used_fallback": False}


def test_relationship_cue_uses_companion_llm_when_real_provider_configured():
    provider = _SpyRealLLMProvider()
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_cue_llm",
        user_id="u_cue_llm",
        user_input="我喜欢听粤剧",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_cue_llm"),
        memory_context=[],
    )

    relationship_cueing_node(state, deps)

    assert provider.payloads
    assert state.draft_reply.startswith("这些粤剧")
    assert "关系编排计划" in (provider.payloads[0].system_prompt or "")
    companion_steps = [a for a in state.agents if a.name == "CompanionAgent"]
    assert len(companion_steps) == 1
    detail = companion_steps[0].detail
    assert detail["relationship_cueing"] is True
    assert detail["llm_generation"]["provider"] == "xiaomimimo"
    assert detail["llm_generation"]["used_fallback"] is False
