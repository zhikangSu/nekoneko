"""Tests for the RoleProfileRegistry (issue #51).

These lock in the product boundaries: eight visible relationship roles, all
non-autonomous, none impersonating family or the deceased, and a boundary
guardian that never role-plays the deceased and never gives medical advice.
"""

from app.relationship.role_profiles import (
    MAX_ROLES_PER_TURN,
    ROLE_PROFILES,
    get_role_profile,
    list_role_profiles,
    list_visible_roles,
)
from app.schemas.relationship import RoleId

EXPECTED_ROLE_IDS = {
    RoleId.same_age_peer,
    RoleId.curious_junior,
    RoleId.middle_age_bridge,
    RoleId.elder_mentor,
    RoleId.theme_companion,
    RoleId.memory_organizer,
    RoleId.boundary_guardian,
    RoleId.no_ai_role,
}


def test_all_eight_roles_listed_and_unique():
    profiles = list_role_profiles()
    assert len(profiles) == 8
    role_ids = [p.role_id for p in profiles]
    assert set(role_ids) == EXPECTED_ROLE_IDS
    # role_id uniqueness
    assert len(set(role_ids)) == 8
    assert profiles == ROLE_PROFILES


def test_boundary_rules_and_best_for_topics_non_empty():
    for profile in list_role_profiles():
        assert profile.boundary_rules, f"{profile.role_id} has no boundary_rules"
        assert all(rule.strip() for rule in profile.boundary_rules)
        if profile.role_id is not RoleId.no_ai_role:
            assert profile.best_for_topics, f"{profile.role_id} has no best_for_topics"


def test_no_role_is_an_autonomous_agent():
    for profile in list_role_profiles():
        assert profile.is_autonomous_agent is False
        assert profile.is_visible_to_user is True


def test_all_roles_are_visible():
    assert list_visible_roles() == ROLE_PROFILES


def test_boundary_guardian_forbids_deceased_impersonation_and_medical_advice():
    guardian = get_role_profile(RoleId.boundary_guardian)
    rules = "".join(guardian.boundary_rules)
    # never role-plays the deceased
    assert "逝者" in rules
    assert any(
        ("逝者" in rule) and (("扮演" in rule) or ("不做" in rule) or ("绝不" in rule))
        for rule in guardian.boundary_rules
    )
    # no medical diagnosis / dosage advice
    assert ("诊断" in rules) or ("剂量" in rules)
    assert any(
        ("诊断" in rule) or ("剂量" in rule) for rule in guardian.boundary_rules
    )


def test_no_role_impersonates_fixed_family_or_the_deceased():
    for profile in list_role_profiles():
        # Labels/functions describe relationship functions, not fixed identities.
        combined = " ".join(
            [
                profile.label_zh,
                profile.label_en,
                profile.relationship_function,
                profile.speaking_style,
                profile.example_opening,
            ]
        )
        # No opening claims to *be* the user's deceased relative.
        assert "我是您" not in profile.example_opening
        assert "我就是" not in profile.example_opening
        # boundary_guardian is the role that owns "never impersonate deceased".
        if profile.role_id is not RoleId.boundary_guardian:
            # Other roles must not claim to be the deceased in their opening line.
            assert "逝者" not in profile.example_opening
        # Non-guardian roles explicitly reference not impersonating real people
        # OR simply never assert a fixed identity in their opening.
        assert "扮演" not in profile.example_opening
        _ = combined  # referenced for clarity; the assertions above are the checks


def test_get_role_profile_returns_correct_profile():
    guardian = get_role_profile(RoleId.boundary_guardian)
    assert guardian.role_id is RoleId.boundary_guardian
    assert guardian.label_en == "Boundary Guardian"
    # string form works too
    by_str = get_role_profile("same_age_peer")
    assert by_str.role_id is RoleId.same_age_peer
    assert by_str.label_zh == "同龄共鸣者"


def test_get_role_profile_raises_on_unknown():
    import pytest

    with pytest.raises(ValueError):
        get_role_profile("not_a_real_role")


def test_no_relationship_role_uses_neutral_companion_opening():
    no_ai = get_role_profile(RoleId.no_ai_role)
    assert no_ai.label_zh == "不使用关系角色"
    assert no_ai.example_opening == "我在听，您想怎么说都可以。"
    assert "固定 AI 人设" in " ".join(no_ai.boundary_rules)


def test_max_roles_per_turn_is_three():
    assert MAX_ROLES_PER_TURN == 3
