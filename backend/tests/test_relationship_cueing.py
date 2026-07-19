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
from app.graph.nodes import companion_node, relationship_cueing_node
from app.graph.state import GraphState
from app.relationship.cue_generator import CueGenerator, is_relationship_cue_turn
from app.relationship.role_profiles import MAX_ROLES_PER_TURN, list_role_profiles
from app.schemas.profile import UserProfile
from app.schemas.relationship import OrchestrationInput, RoleId, RoleSelectionMode
from app.services.llm_provider import CompanionReplyInput, LLMProvider


# Chinese labels for the visible roles, so tests can count role lines and assert
# distinct labels without hardcoding role internals.
_ROLE_LABELS = [p.label_zh for p in list_role_profiles()]


def _route(body: dict) -> str:
    return body["agent_trace"]["route"]


def _triage_action(step: dict) -> str | None:
    return step["detail"].get("decision", {}).get("action")


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
    requested_roles = [
        "curious_junior",
        "theme_companion",
        "same_age_peer",
    ]
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_manual_roles",
            "message": "看到这个老电视，我想起以前的日子",
            "role_selection_mode": "manual",
            "selected_role_ids": requested_roles,
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    orch = [
        a
        for a in body["agent_trace"]["agents"]
        if a["name"] == "RelationshipOrchestratorAgent"
    ]
    assert orch[0]["detail"]["role_selection_mode"] == "manual"
    assert orch[0]["detail"]["requested_role_ids"] == requested_roles
    assert orch[0]["detail"]["selected_roles"] == requested_roles
    assert [m["role_id"] for m in body["role_messages"]] == requested_roles
    assert "晚辈好奇者：" in body["response_text"]
    assert "主题陪伴者：" in body["response_text"]
    assert "同龄共鸣者：" in body["response_text"]


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
    assert "给我们讲讲" not in body["response_text"]
    assert "跟我们说说" not in body["response_text"]
    assert "不想说也没关系" not in body["response_text"]

    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["topic_id"] == "T05"
    assert metadata["material_type"] == "topic_card"
    assert "same_age_peer" in metadata["selected_roles"]
    assert metadata["cueing_style"] == "agent_agent_then_invite"


def test_fake_topic_card_greeting_acknowledges_user_before_topic(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_greeting_fake",
            "message": "你们好啊",
            "topic_id": "T06",
            "topic_label": "老电影、戏曲、歌曲、地方文化",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    assert body["role_messages"][0]["text"] == "您好呀，我们都在，见到您很高兴。"
    assert all(
        "粤剧" not in message["text"] for message in body["role_messages"]
    )
    orchestrator = next(
        step
        for step in body["agent_trace"]["agents"]
        if step["name"] == "RelationshipOrchestratorAgent"
    )
    assert orchestrator["detail"]["topic_card_greeting"] is True
    assert all(
        step["name"] != "CompanionAgent"
        for step in body["agent_trace"]["agents"]
    )


def test_learning_topic_card_introduces_concrete_learning_scene(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_learning",
            "message": "聊这个吧",
            "topic_id": "T01",
            "topic_label": "年轻时的学习经历",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    text = body["response_text"]
    assert len(body["role_messages"]) == 3
    assert any(word in text for word in ("读书", "上学", "学校", "老师", "同学"))
    assert "想聊什么都行" not in text
    assert "接着刚才说的" not in text
    assert "听前面这么一说" not in text
    assert "您这份经历" not in text
    assert "最让您记得" not in text
    assert "带孩子" not in text
    assert "孙辈" not in text
    assert body["agent_trace"]["research_trace"]["topic"]["classified_topic"] == (
        "study_learning"
    )


def test_work_topic_card_opening_does_not_assume_elder_story(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_work",
            "message": "聊这个吧",
            "topic_id": "T02",
            "topic_label": "年轻时的工作经历",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    text = body["response_text"]
    assert len(body["role_messages"]) == 3
    assert any(word in text for word in ("工作", "单位", "车间", "同事", "上班"))
    assert "接着刚才说的" not in text
    assert "听前面这么一说" not in text
    assert "您这份经历" not in text
    assert "最让您记得" not in text
    assert body["agent_trace"]["research_trace"]["topic"]["classified_topic"] == (
        "work_collective"
    )
    orch = [
        a
        for a in body["agent_trace"]["agents"]
        if a["name"] == "RelationshipOrchestratorAgent"
    ]
    assert orch[0]["detail"]["topic_card_opening"] is True


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
    assert first_two_labels == ["同龄共鸣者", "中年传承者"]
    assert body["role_messages"][2]["role_label"] == "晚辈好奇者"
    assert body["role_messages"][1]["text"].startswith("是啊")
    assert body["role_messages"][2]["text"].startswith("听前面这么一说")

    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["cueing_style"] == "agent_agent_then_invite"
    assert metadata["selected_roles"] == [
        "same_age_peer",
        "middle_age_bridge",
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


def test_topic_card_refusal_keeps_multi_role_cast_and_stops_old_topic(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_refusal",
            "message": "不想聊这个话题",
            "topic_id": "T05",
            "topic_label": "老照片或旧物件",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    assert [message["role_id"] for message in body["role_messages"]] == [
        "same_age_peer",
        "middle_age_bridge",
        "curious_junior",
    ]
    assert len({message["text"] for message in body["role_messages"]}) == 3
    assert all("？" not in message["text"] for message in body["role_messages"])
    assert all("老照片" not in message["text"] for message in body["role_messages"])
    assert all("旧物" not in message["text"] for message in body["role_messages"])

    orchestrator = next(
        step
        for step in body["agent_trace"]["agents"]
        if step["name"] == "RelationshipOrchestratorAgent"
    )
    assert orchestrator["detail"]["topic_card_refusal"] is True
    assert orchestrator["detail"]["cueing_style"] == "boundary_acknowledgement"
    assert "角色阵容保持不变" in orchestrator["detail"]["boundary_trace"]
    assert any(
        "停止延续" in note
        for note in body["agent_trace"]["research_trace"]["boundary"][
            "boundary_notes"
        ]
    )

    triage = [
        step
        for step in body["agent_trace"]["tools"]
        if step["name"] == "MemoryTriagePolicy"
        and _triage_action(step) == "create_boundary_card"
    ]
    assert len(triage) == 1
    assert triage[0]["detail"]["memory_card_id"]


def test_topic_card_refusal_preserves_user_selected_role_order(client):
    requested_roles = ["curious_junior", "elder_mentor"]
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_refusal_manual",
            "message": "今天不太想说，可以吗",
            "topic_id": "T01",
            "topic_label": "年轻时的学习经历",
            "material_type": "topic_card",
            "role_selection_mode": "manual",
            "selected_role_ids": requested_roles,
        },
    ).json()

    assert _route(body) == "relationship_cueing"
    assert [message["role_id"] for message in body["role_messages"]] == requested_roles
    assert all("？" not in message["text"] for message in body["role_messages"])
    metadata = body["agent_trace"]["research_metadata"]
    assert metadata["selected_roles"] == requested_roles
    assert metadata["cueing_style"] == "boundary_acknowledgement"


def test_topic_card_relationship_strain_is_not_replaced_by_card_seed(client):
    body = client.post(
        "/api/chat",
        json={
            "user_id": "cue_topic_card_relationship_strain",
            "message": "儿子不理我，聊这个吧",
            "topic_id": "T05",
            "topic_label": "老照片或旧物件",
            "material_type": "topic_card",
        },
    ).json()

    assert _route(body) == "companion_chat"
    assert body["role_messages"] == []


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
    triage = [t for t in tools if t["name"] == "MemoryTriagePolicy"][-1]
    assert triage["detail"]["saved"] is True
    assert triage["detail"]["saved_memory_id"]

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
    orch = [
        a
        for a in body["agent_trace"]["agents"]
        if a["name"] == "RelationshipOrchestratorAgent"
    ]
    assert len(orch) == 1
    assert orch[0]["detail"]["auto_role_style"] is True


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
        self.reply_text = "这些粤剧老段子听起来很有味道。您最喜欢的是哪一段呀？"
        self.reply_texts: list[str] = []

    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        self.payloads.append(payload)
        if self.reply_texts:
            return self.reply_texts.pop(0)
        return self.reply_text

    @property
    def generation_info(self) -> dict:
        return {"provider": self.name, "model": "test", "used_fallback": False}


def test_relationship_cue_uses_companion_llm_when_real_provider_configured():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "同龄共鸣者：粤剧一响起来，老戏院里的热闹劲儿好像也跟着回来了。\n"
        "中年传承者：这些唱腔把地方的声音和一代人的生活都留了下来。\n"
        "晚辈好奇者：听前面这么一说，我也好奇您最喜欢哪一段？"
    )
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
    assert "关系编排计划" in (provider.payloads[0].system_prompt or "")
    assert "必须让每个角色分别说一句" in (provider.payloads[0].system_prompt or "")
    assert [m.role_label for m in state.role_messages] == [
        "同龄共鸣者",
        "中年传承者",
        "晚辈好奇者",
    ]
    companion_steps = [a for a in state.agents if a.name == "CompanionAgent"]
    assert len(companion_steps) == 1
    detail = companion_steps[0].detail
    assert detail["relationship_cueing"] is True
    assert detail["llm_generation"]["provider"] == "xiaomimimo"
    assert detail["llm_generation"]["used_fallback"] is False
    assert detail["llm_role_reply_accepted"] is True
    assert detail["llm_role_reply_retry_used"] is False
    assert detail["llm_role_reply_fallback_used"] is False


def test_topic_card_start_uses_real_llm_when_configured():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "同龄共鸣者：说起上学，我们那时候一本课本常常要翻上好多遍。\n"
        "中年传承者：这些读书经历里，也留着当时学校和家庭的生活印记。\n"
        "晚辈好奇者：刚才两位说得真有画面，我想知道您最先想到哪位老师？"
    )
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_topic_card_intro",
        user_id="u_topic_card_intro",
        user_input="聊这个吧",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_topic_card_intro"),
        memory_context=[],
        topic_id="T01",
        topic_label="年轻时的学习经历",
    )

    relationship_cueing_node(state, deps)

    assert len(provider.payloads) == 1
    assert provider.payloads[0].message == "聊这个吧"
    assert "offline_template_for_reference" in (
        provider.payloads[0].system_prompt or ""
    )
    assert "上面的 topic 是系统提供的背景" in (
        provider.payloads[0].system_prompt or ""
    )
    assert [m.role_label for m in state.role_messages] == [
        "同龄共鸣者",
        "中年传承者",
        "晚辈好奇者",
    ]
    assert state.draft_reply == provider.reply_text
    assert "读书" in state.draft_reply or "上学" in state.draft_reply
    assert "想聊什么都行" not in state.draft_reply
    assert "接着刚才说的" not in state.draft_reply
    assert "听前面这么一说" not in state.draft_reply
    assert "您这份经历" not in state.draft_reply
    assert "最让您记得" not in state.draft_reply
    companion_step = next(
        step for step in state.agents if step.name == "CompanionAgent"
    )
    assert companion_step.detail["llm_role_reply_accepted"] is True
    assert companion_step.detail["llm_role_reply_fallback_used"] is False
    assert companion_step.detail["companion_input_source"] == "raw_user_input"
    assert companion_step.detail["topic_card_greeting"] is False


def test_topic_card_greeting_retries_when_real_llm_ignores_user():
    provider = _SpyRealLLMProvider()
    repaired_reply = (
        "同龄共鸣者：您好呀，我们都在，见到您很高兴。\n"
        "中年传承者：您好，咱们不着急，先按您舒服的节奏来。\n"
        "晚辈好奇者：您好呀，您想先聊这张话题卡，还是随意说两句都可以。"
    )
    provider.reply_texts = [
        (
            "同龄共鸣者：粤剧一响起来，街头巷尾都像回到从前了。\n"
            "中年传承者：这些老戏老曲一代代传下来，确实有自己的味道。\n"
            "晚辈好奇者：我挺好奇的，您平时最喜欢听哪出戏呀？"
        ),
        repaired_reply,
    ]
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_topic_card_greeting_llm",
        user_id="u_topic_card_greeting_llm",
        user_input="你们好啊",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_topic_card_greeting_llm"),
        memory_context=[],
        topic_id="T06",
        topic_label="老电影、戏曲、歌曲、地方文化",
    )

    relationship_cueing_node(state, deps)

    assert len(provider.payloads) == 2
    assert all(payload.message == "你们好啊" for payload in provider.payloads)
    assert "上面的 topic 是系统提供的背景" in (
        provider.payloads[0].system_prompt or ""
    )
    assert "第一位角色必须先自然回应用户的问候" in (
        provider.payloads[1].system_prompt or ""
    )
    assert state.draft_reply == repaired_reply
    detail = next(
        step.detail for step in state.agents if step.name == "CompanionAgent"
    )
    assert detail["companion_input_source"] == "raw_user_input"
    assert detail["topic_card_greeting"] is True
    assert detail["llm_role_reply_initial_rejection_reason"] == (
        "topic_card_greeting_not_acknowledged"
    )
    assert detail["llm_role_reply_retry_used"] is True
    assert detail["llm_role_reply_retry_accepted"] is True
    assert detail["llm_role_reply_fallback_used"] is False


def test_topic_card_refusal_uses_real_llm_with_multi_role_boundary_prompt():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "同龄共鸣者：好，这个我们就先放下，不勉强您。\n"
        "中年传承者：明白，照您觉得自在的方式来最合适。\n"
        "晚辈好奇者：好呀，我也不再追问，安静一会儿也没关系。"
    )
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_topic_card_refusal_llm",
        user_id="u_topic_card_refusal_llm",
        user_input="先不聊这个吧",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_topic_card_refusal_llm"),
        memory_context=[],
        topic_id="T05",
        topic_label="老照片或旧物件",
    )

    relationship_cueing_node(state, deps)

    assert provider.payloads
    prompt = provider.payloads[0].system_prompt or ""
    assert "用户已经明确拒绝当前话题" in prompt
    assert "不得继续展开被拒绝的话题" in prompt
    assert "不得提出问题" in prompt
    assert provider.payloads[0].message == "先不聊这个吧"
    assert [message.role_id for message in state.role_messages] == [
        RoleId.same_age_peer,
        RoleId.middle_age_bridge,
        RoleId.curious_junior,
    ]
    assert state.draft_reply == provider.reply_text


def test_pressuring_real_llm_topic_refusal_reply_falls_back_to_safe_roles():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "同龄共鸣者：好，那您还记得照片里的人吗？\n"
        "中年传承者：这段经历还是很值得继续说。\n"
        "晚辈好奇者：您愿意再讲讲吗？"
    )
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_topic_card_refusal_fallback",
        user_id="u_topic_card_refusal_fallback",
        user_input="不想聊这个话题",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_topic_card_refusal_fallback"),
        memory_context=[],
        topic_id="T05",
        topic_label="老照片或旧物件",
    )

    relationship_cueing_node(state, deps)

    assert len(provider.payloads) == 2
    assert "上一版回复没有满足" in provider.payloads[1].system_prompt
    assert "不得提出问题" in provider.payloads[1].system_prompt
    assert state.draft_reply != provider.reply_text
    assert len(state.role_messages) == 3
    assert all("？" not in message.text for message in state.role_messages)
    companion_step = next(
        step for step in state.agents if step.name == "CompanionAgent"
    )
    assert companion_step.detail["llm_role_reply_accepted"] is False
    assert (
        companion_step.detail["llm_role_reply_final_rejection_reason"]
        == "topic_refusal_reply_pressures_user"
    )
    assert companion_step.detail["llm_role_reply_retry_used"] is True
    assert companion_step.detail["llm_role_reply_retry_accepted"] is False
    assert companion_step.detail["llm_role_reply_fallback_used"] is True


def test_real_relationship_cue_parses_llm_role_lines_instead_of_templates():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "中年传承者：这些粤剧唱段里有很多老街坊的味道，听您提起来很亲切。\n"
        "同龄共鸣者：我们那时候听戏，常常一听前奏就知道是哪一段。\n"
        "晚辈好奇者：您最记得的是哪一段？我想听听。"
    )
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_cue_llm_roles",
        user_id="u_cue_llm_roles",
        user_input="我喜欢听粤剧",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_cue_llm_roles"),
        memory_context=[],
    )

    relationship_cueing_node(state, deps)

    assert state.draft_reply != provider.reply_text
    assert [m.role_label for m in state.role_messages] == [
        "同龄共鸣者",
        "中年传承者",
        "晚辈好奇者",
    ]
    assert state.role_messages[0].text.startswith("我们那时候听戏")
    assert state.role_messages[1].text.startswith("这些粤剧唱段里")


def test_real_relationship_cue_retries_malformed_reply_before_fallback():
    provider = _SpyRealLLMProvider()
    provider.reply_text = "同龄共鸣者：粤剧啊，我们"
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_cue_llm_malformed",
        user_id="u_cue_llm_malformed",
        user_input="我喜欢听粤剧",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_cue_llm_malformed"),
        memory_context=[],
    )

    relationship_cueing_node(state, deps)

    assert len(provider.payloads) == 2
    assert "上一版回复没有满足" in provider.payloads[1].system_prompt
    assert state.draft_reply != provider.reply_text
    assert [m.role_label for m in state.role_messages] == [
        "同龄共鸣者",
        "中年传承者",
        "晚辈好奇者",
    ]
    assert all(
        not message.text.endswith(("我们", "就", "，"))
        for message in state.role_messages
    )
    companion_steps = [a for a in state.agents if a.name == "CompanionAgent"]
    detail = companion_steps[0].detail
    assert detail["llm_role_reply_accepted"] is False
    assert detail["llm_role_reply_initial_rejection_reason"] == (
        "expected_3_role_lines_got_1"
    )
    assert detail["llm_role_reply_final_rejection_reason"] == (
        "expected_3_role_lines_got_1"
    )
    assert detail["llm_role_reply_retry_used"] is True
    assert detail["llm_role_reply_retry_accepted"] is False
    assert detail["llm_role_reply_fallback_used"] is True


def test_real_relationship_cue_accepts_repaired_role_reply():
    provider = _SpyRealLLMProvider()
    repaired_reply = (
        "同龄共鸣者：粤剧一响起来，熟悉的调子就回来了。\n"
        "中年传承者：听前面这么一说，这些唱段也留住了地方生活的记忆。\n"
        "晚辈好奇者：我也想听听，您最喜欢的是哪一段？"
    )
    provider.reply_texts = [
        (
            "同龄共鸣者：粤剧一响起来，熟悉的调子就回来了。\n"
            "晚辈好奇者：听着就很有老街坊一起看戏的感觉。"
        ),
        repaired_reply,
    ]
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_cue_llm_repaired",
        user_id="u_cue_llm_repaired",
        user_input="我喜欢听粤剧",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_cue_llm_repaired"),
        memory_context=[],
    )

    relationship_cueing_node(state, deps)

    assert len(provider.payloads) == 2
    assert [m.role_label for m in state.role_messages] == [
        "同龄共鸣者",
        "中年传承者",
        "晚辈好奇者",
    ]
    assert state.draft_reply == repaired_reply
    detail = next(
        step.detail for step in state.agents if step.name == "CompanionAgent"
    )
    assert detail["llm_role_reply_initial_rejection_reason"] == (
        "expected_3_role_lines_got_2"
    )
    assert detail["llm_role_reply_final_rejection_reason"] is None
    assert detail["llm_role_reply_retry_used"] is True
    assert detail["llm_role_reply_retry_accepted"] is True
    assert detail["llm_role_reply_fallback_used"] is False


def test_companion_chat_multi_role_reply_becomes_separate_role_messages():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "同龄共鸣者：聊工作啊，我们那会儿在单位里忙起来，确实有累也有热闹。\n"
        "晚辈好奇者：我有点好奇，您那时候最常做的是哪一类活儿？\n"
        "中年传承者：这些在岗位上熬出来的经验，后来回头看很有分量。"
    )
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
    )
    state = GraphState(
        turn_id="t_companion_multi_roles",
        user_id="u_companion_multi_roles",
        user_input="聊聊工作，以前在单位里的日子",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_companion_multi_roles"),
        memory_context=[],
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=[
            RoleId.same_age_peer,
            RoleId.curious_junior,
            RoleId.middle_age_bridge,
        ],
    )

    companion_node(state, deps)

    assert "必须让每个角色分别说一句" in provider.payloads[0].system_prompt
    assert "第二位必须接上一位的意思继续说" in provider.payloads[0].system_prompt
    assert "最后一位再把话题自然递给用户" in provider.payloads[0].system_prompt
    assert "不要使用“您们”" in provider.payloads[0].system_prompt
    assert [message.role_label for message in state.role_messages] == [
        "同龄共鸣者",
        "晚辈好奇者",
        "中年传承者",
    ]
    assert state.role_messages[0].text.startswith("聊工作啊")


def test_companion_chat_retries_when_manual_role_is_missing():
    provider = _SpyRealLLMProvider()
    provider.reply_texts = [
        (
            "同龄共鸣者：机器一响起来，说话确实得靠默契。\n"
            "晚辈好奇者：听着就能想见当时车间里的热闹。"
        ),
        (
            "同龄共鸣者：机器一响起来，说话确实得靠默契。\n"
            "晚辈好奇者：听前面这么一说，我也能想见当时车间里的热闹。\n"
            "中年传承者：这些在忙碌里磨出来的配合，也是很珍贵的经验。"
        ),
    ]
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    selected_roles = [
        RoleId.same_age_peer,
        RoleId.curious_junior,
        RoleId.middle_age_bridge,
    ]
    state = GraphState(
        turn_id="t_companion_retry_missing_role",
        user_id="u_companion_retry_missing_role",
        user_input="我们那时候说话常靠打手势",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_companion_retry_missing_role"),
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=selected_roles,
    )

    companion_node(state, deps)

    assert len(provider.payloads) == 2
    assert "上一版回复没有满足" in provider.payloads[1].system_prompt
    assert [message.role_id for message in state.role_messages] == selected_roles
    companion_step = next(step for step in state.agents if step.name == "CompanionAgent")
    assert companion_step.detail["llm_role_reply_retry_used"] is True
    assert companion_step.detail["llm_role_reply_retry_accepted"] is True
    assert companion_step.detail["llm_role_reply_fallback_used"] is False
    assert (
        companion_step.detail["llm_role_reply_initial_rejection_reason"]
        == "expected_3_role_lines_got_2"
    )


def test_companion_chat_reorders_roles_and_normalizes_unpleasant_plural():
    provider = _SpyRealLLMProvider()
    provider.reply_text = (
        "中年传承者：您们在车间磨出来的配合，是很珍贵的经验。\n"
        "同龄共鸣者：机器一响起来，我们那会儿也常靠手势交流。\n"
        "晚辈好奇者：听前面这么一说，我也能想见当时忙碌的样子。"
    )
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    selected_roles = [
        RoleId.same_age_peer,
        RoleId.curious_junior,
        RoleId.middle_age_bridge,
    ]
    state = GraphState(
        turn_id="t_companion_role_order",
        user_id="u_companion_role_order",
        user_input="我们那时候说话常靠打手势",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_companion_role_order"),
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=selected_roles,
    )

    companion_node(state, deps)

    assert len(provider.payloads) == 1
    assert [message.role_id for message in state.role_messages] == selected_roles
    assert "您们" not in state.draft_reply
    assert "大家在车间" in state.draft_reply
    assert state.draft_reply.splitlines()[0].startswith("同龄共鸣者：")
    assert state.draft_reply.splitlines()[1].startswith("晚辈好奇者：")
    assert state.draft_reply.splitlines()[2].startswith("中年传承者：")
    companion_step = next(step for step in state.agents if step.name == "CompanionAgent")
    assert companion_step.detail["llm_role_reply_retry_used"] is False
    assert companion_step.detail["llm_role_reply_normalized_terms"] == ["您们"]


def test_companion_chat_single_manual_role_keeps_visible_identity():
    provider = _SpyRealLLMProvider()
    provider.reply_text = "长辈引导者：慢慢来，想到哪儿说到哪儿，您舒服最要紧。"
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    state = GraphState(
        turn_id="t_companion_single_role",
        user_id="u_companion_single_role",
        user_input="我想慢慢聊聊以前的事",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_companion_single_role"),
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=[RoleId.elder_mentor],
    )

    companion_node(state, deps)

    assert "严格只输出 1 行" in provider.payloads[0].system_prompt
    assert [message.role_id for message in state.role_messages] == [
        RoleId.elder_mentor
    ]
    assert state.role_messages[0].role_label == "长辈引导者"
    assert "陪伴 AI" not in state.draft_reply


def test_companion_chat_uses_complete_role_fallback_after_failed_retry():
    provider = _SpyRealLLMProvider()
    incomplete_reply = (
        "同龄共鸣者：机器一响起来，说话确实得靠默契。\n"
        "晚辈好奇者：听着就能想见当时车间里的热闹。"
    )
    provider.reply_texts = [incomplete_reply, incomplete_reply]
    deps = SimpleNamespace(
        companion=CompanionAgent(provider),
        relationship_orchestrator=RelationshipOrchestratorAgent(),
        cue_generator=CueGenerator(),
    )
    selected_roles = [
        RoleId.same_age_peer,
        RoleId.curious_junior,
        RoleId.middle_age_bridge,
    ]
    state = GraphState(
        turn_id="t_companion_role_fallback",
        user_id="u_companion_role_fallback",
        user_input="我们那时候说话常靠打手势",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="u_companion_role_fallback"),
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=selected_roles,
    )

    companion_node(state, deps)

    assert len(provider.payloads) == 2
    assert [message.role_id for message in state.role_messages] == selected_roles
    assert len(state.role_messages) == 3
    companion_step = next(step for step in state.agents if step.name == "CompanionAgent")
    assert companion_step.detail["llm_role_reply_retry_accepted"] is False
    assert companion_step.detail["llm_role_reply_fallback_used"] is True
