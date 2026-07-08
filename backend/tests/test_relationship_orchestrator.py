"""Tests for the RelationshipOrchestratorAgent + topic classifier + policy (#52).

Covers >=5 topic categories, the three acceptance examples, the sensitive
boundary path, preference overrides, and cross-cutting invariants. Rule-based
and deterministic — no network / LLM.
"""

from __future__ import annotations

from app.agents.relationship_orchestrator import RelationshipOrchestratorAgent
from app.relationship.orchestration_policy import decide
from app.relationship.role_profiles import (
    MAX_ROLES_PER_TURN,
    list_role_profiles,
)
from app.relationship.topic_classifier import (
    SENSITIVE_TOPICS,
    Topic,
    classify_topic,
)
from app.schemas.relationship import (
    CueingStyle,
    OrchestrationInput,
    RelationshipDecision,
    RoleId,
    RoleSelectionMode,
)

REGISTRY_IDS = {p.role_id for p in list_role_profiles()}


def _orchestrate(text: str, **kwargs) -> RelationshipDecision:
    agent = RelationshipOrchestratorAgent()
    return agent.orchestrate(OrchestrationInput(user_input=text, **kwargs))


def _assert_common_invariants(decision: RelationshipDecision) -> None:
    # selected_roles length within [1, 3]
    assert 1 <= len(decision.selected_roles) <= MAX_ROLES_PER_TURN
    # never exceeds 3
    assert len(decision.selected_roles) <= 3
    # all selected are valid registry roles
    for role in decision.selected_roles:
        assert role in REGISTRY_IDS
    # no duplicates
    assert len(decision.selected_roles) == len(set(decision.selected_roles))
    # no_ai_role never sits beside a speaking role
    if RoleId.no_ai_role in decision.selected_roles:
        assert decision.selected_roles == [RoleId.no_ai_role]
    # primary (when set) is among selected
    if decision.primary_role is not None:
        assert decision.primary_role in decision.selected_roles
    # the four trace strings and the visible summary are non-empty
    assert decision.role_trace.strip()
    assert decision.topic_trace.strip()
    assert decision.memory_trace.strip()
    assert decision.boundary_trace.strip()
    assert decision.trace_visible_summary.strip()
    assert decision.role_selection_reason.strip()


# --------------------------------------------------------------------------- #
# Topic classifier                                                            #
# --------------------------------------------------------------------------- #


def test_classifier_covers_core_topics():
    assert classify_topic("看到老电视想起以前") is Topic.old_object_photo
    assert classify_topic("我年轻时在工厂车间上班") is Topic.work_collective
    assert classify_topic("聊聊我孙子的教育") is Topic.family_education
    assert classify_topic("我喜欢粤剧") is Topic.culture_arts
    assert classify_topic("我想起已经离开的老伴") is Topic.deceased_grief
    assert classify_topic("我最近身体不好在住院") is Topic.health_care
    assert classify_topic("家里闹矛盾，是我的隐私") is Topic.privacy_family_conflict
    assert classify_topic("一个人在家，觉得没意思") is Topic.loneliness_mood
    assert classify_topic("总想起从前那些回忆") is Topic.general_reminiscence
    assert classify_topic("今天天气怎么样") is Topic.other
    assert classify_topic("") is Topic.other


def test_sensitive_keywords_take_priority_over_cheerful_ones():
    # grief co-occurring with a pleasant topic still classifies as sensitive
    assert classify_topic("看着老照片，想起走了的老伴") is Topic.deceased_grief
    assert Topic.deceased_grief in SENSITIVE_TOPICS
    assert Topic.health_care in SENSITIVE_TOPICS
    assert Topic.privacy_family_conflict in SENSITIVE_TOPICS


# --------------------------------------------------------------------------- #
# Acceptance examples                                                          #
# --------------------------------------------------------------------------- #


def test_accept_old_tv_reminiscence_uses_peer_set_agent_agent():
    d = _orchestrate("看到老电视想起以前")
    assert RoleId.same_age_peer in d.selected_roles
    assert RoleId.curious_junior in d.selected_roles
    assert RoleId.middle_age_bridge in d.selected_roles
    assert d.cueing_style == CueingStyle.agent_agent_then_invite
    assert d.role_selection_reason.strip()
    _assert_common_invariants(d)


def test_accept_deceased_partner_is_boundary_path():
    d = _orchestrate("我想起已经离开的老伴")
    assert d.cueing_style != CueingStyle.agent_agent_then_invite
    assert d.cueing_style == CueingStyle.no_cue
    assert RoleId.boundary_guardian in d.selected_roles
    notes = " ".join(d.boundary_notes)
    assert ("逝者" in notes) or ("不扮演" in notes)
    assert d.should_generate_memory_card is False
    _assert_common_invariants(d)


def test_accept_yueju_uses_theme_or_peer():
    d = _orchestrate("我喜欢粤剧")
    assert (RoleId.theme_companion in d.selected_roles) or (
        RoleId.same_age_peer in d.selected_roles
    )
    assert RoleId.theme_companion in d.selected_roles
    assert RoleId.same_age_peer in d.selected_roles
    assert RoleId.curious_junior in d.selected_roles
    assert len(d.selected_roles) >= 3
    assert d.cueing_style == CueingStyle.agent_agent_then_invite
    _assert_common_invariants(d)


# --------------------------------------------------------------------------- #
# Per-topic role routing                                                       #
# --------------------------------------------------------------------------- #


def test_family_education_uses_junior_and_bridge():
    d = _orchestrate("想聊聊孩子的教育和儿女")
    assert RoleId.same_age_peer in d.selected_roles
    assert RoleId.curious_junior in d.selected_roles
    assert RoleId.middle_age_bridge in d.selected_roles
    assert len(d.selected_roles) >= 3
    assert d.primary_role is RoleId.middle_age_bridge
    assert d.cueing_style == CueingStyle.agent_agent_then_invite
    _assert_common_invariants(d)


def test_work_collective_uses_peer_set():
    d = _orchestrate("那会儿在厂里车间跟老同事一起上班")
    for role in (RoleId.same_age_peer, RoleId.curious_junior, RoleId.middle_age_bridge):
        assert role in d.selected_roles
    assert d.primary_role is RoleId.same_age_peer
    _assert_common_invariants(d)


def test_general_reminiscence_uses_peer_set():
    d = _orchestrate("总想起以前的事")
    assert d.topic == Topic.general_reminiscence.value
    assert RoleId.same_age_peer in d.selected_roles
    assert d.cueing_style == CueingStyle.agent_agent_then_invite
    _assert_common_invariants(d)


def test_loneliness_mood_is_gentle_single_prelude():
    d = _orchestrate("一个人在家，觉得没意思")
    assert RoleId.elder_mentor in d.selected_roles
    assert d.primary_role is RoleId.elder_mentor
    assert d.cueing_style == CueingStyle.single_role_prelude
    _assert_common_invariants(d)


# --------------------------------------------------------------------------- #
# Sensitive boundary path                                                      #
# --------------------------------------------------------------------------- #


def test_health_topic_is_boundary_path_no_agent_agent():
    d = _orchestrate("我最近身体不好，一直在吃药住院")
    assert d.cueing_style == CueingStyle.no_cue
    assert d.cueing_style != CueingStyle.agent_agent_then_invite
    assert RoleId.boundary_guardian in d.selected_roles
    notes = " ".join(d.boundary_notes)
    assert ("诊断" in notes) or ("剂量" in notes)
    assert d.should_generate_memory_card is False
    _assert_common_invariants(d)


def test_privacy_conflict_is_boundary_path():
    d = _orchestrate("家里闹矛盾，这是我的隐私")
    assert d.cueing_style == CueingStyle.no_cue
    assert RoleId.boundary_guardian in d.selected_roles
    assert d.should_generate_memory_card is False
    _assert_common_invariants(d)


def test_risk_flags_force_boundary_path_even_when_topic_light():
    # A light topic on the surface but risk_flags flag a health concern.
    d = _orchestrate(
        "随便聊聊",
        risk_flags={"health": True},
    )
    assert d.cueing_style == CueingStyle.no_cue
    assert RoleId.boundary_guardian in d.selected_roles
    _assert_common_invariants(d)


# --------------------------------------------------------------------------- #
# Overrides                                                                    #
# --------------------------------------------------------------------------- #


def test_long_specific_narrative_uses_single_role_direct():
    long_text = (
        "我年轻的时候在工厂车间上班，那会儿每天天不亮就骑车去厂里，"
        "跟老同事们一起干活，中午在食堂吃饭，下班还一起打球，特别热闹充实。"
    )
    assert len(long_text) >= 60
    d = _orchestrate(long_text)
    assert d.cueing_style == CueingStyle.direct
    assert len(d.selected_roles) == 1
    assert d.selected_roles[0] == d.primary_role
    _assert_common_invariants(d)


def test_pref_dislikes_follow_up_drops_curious_junior():
    d = _orchestrate(
        "看到老电视想起以前",
        user_role_preferences={"dislike_follow_up": True},
    )
    assert RoleId.curious_junior not in d.selected_roles
    _assert_common_invariants(d)


def test_pref_no_ai_selects_no_ai_role_only():
    d = _orchestrate(
        "看到老电视想起以前",
        user_role_preferences={"only_self_narrate": True},
    )
    assert d.selected_roles == [RoleId.no_ai_role]
    assert d.cueing_style == CueingStyle.no_cue
    assert d.should_generate_memory_card is False
    _assert_common_invariants(d)


def test_manual_role_selection_uses_requested_roles():
    d = _orchestrate(
        "看到老电视想起以前",
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=[RoleId.same_age_peer, RoleId.curious_junior],
    )
    assert d.selected_roles == [RoleId.same_age_peer, RoleId.curious_junior]
    assert d.primary_role is RoleId.same_age_peer
    assert d.cueing_style == CueingStyle.agent_agent_then_invite
    assert "用户手动选择" in d.role_selection_reason
    _assert_common_invariants(d)


def test_manual_no_ai_role_is_exclusive():
    d = _orchestrate(
        "看到老电视想起以前",
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=[RoleId.same_age_peer, RoleId.no_ai_role],
    )
    assert d.selected_roles == [RoleId.no_ai_role]
    assert d.cueing_style == CueingStyle.no_cue
    assert d.should_generate_memory_card is False
    _assert_common_invariants(d)


def test_manual_empty_selection_falls_back_to_auto():
    d = _orchestrate(
        "看到老电视想起以前",
        role_selection_mode=RoleSelectionMode.manual,
        selected_role_ids=[],
    )
    assert RoleId.same_age_peer in d.selected_roles
    assert RoleId.curious_junior in d.selected_roles
    assert RoleId.middle_age_bridge in d.selected_roles
    assert "用户手动选择" not in d.role_selection_reason
    _assert_common_invariants(d)


def test_memory_context_recorded_in_trace():
    d = _orchestrate(
        "看到老电视想起以前",
        memory_context=["老人年轻时是电视厂工人"],
    )
    assert "老人年轻时是电视厂工人" in d.memory_trace
    d2 = _orchestrate("看到老电视想起以前")
    assert d2.memory_trace == "未使用记忆"


def test_memory_card_only_for_clear_nonsensitive_personal_topics():
    assert _orchestrate("看到老电视想起以前").should_generate_memory_card is True
    assert _orchestrate("我喜欢粤剧").should_generate_memory_card is True
    # sensitive topics never generate a memory card
    assert _orchestrate("我想起已经离开的老伴").should_generate_memory_card is False
    assert _orchestrate("我最近身体不好在住院").should_generate_memory_card is False


# --------------------------------------------------------------------------- #
# Cross-cutting invariants                                                     #
# --------------------------------------------------------------------------- #


def test_sensitive_topics_never_use_agent_agent_cue():
    sensitive_inputs = [
        "我想起已经离开的老伴",
        "我最近身体不好在住院吃药",
        "家里闹矛盾这是隐私",
    ]
    for text in sensitive_inputs:
        d = _orchestrate(text)
        assert d.cueing_style != CueingStyle.agent_agent_then_invite
        _assert_common_invariants(d)


def test_all_decisions_hold_invariants_across_topics():
    samples = [
        "看到老电视想起以前",
        "那会儿在厂里上班",
        "聊聊孩子的教育",
        "我喜欢京剧和老电影",
        "我想起走了的老伴",
        "身体不好在吃药",
        "家里闹矛盾，隐私",
        "一个人觉得没意思",
        "总想起从前",
        "今天天气怎么样",
    ]
    for text in samples:
        _assert_common_invariants(_orchestrate(text))


def test_custom_registry_never_selects_unknown_roles():
    # A shrunk registry: policy must never pick a role that is not present.
    profiles = [p for p in list_role_profiles() if p.role_id in {
        RoleId.same_age_peer,
        RoleId.boundary_guardian,
        RoleId.elder_mentor,
    }]
    agent = RelationshipOrchestratorAgent(roles=profiles)
    d = agent.orchestrate(OrchestrationInput(user_input="看到老电视想起以前"))
    allowed = {p.role_id for p in profiles}
    for role in d.selected_roles:
        assert role in allowed
    _assert_common_invariants(d)


def test_decide_is_deterministic():
    inp = OrchestrationInput(user_input="看到老电视想起以前")
    roles = list_role_profiles()
    d1 = decide(inp, classify_topic(inp.user_input), roles)
    d2 = decide(inp, classify_topic(inp.user_input), roles)
    assert d1 == d2
