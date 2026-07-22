from types import SimpleNamespace

from app.core.constants import CompanionMode
from app.graph.nodes import output_guard_node
from app.graph.state import GraphState
from app.schemas.profile import UserProfile
from app.schemas.relationship import RoleCueMessage, RoleId
from app.tools.output_rule_guard import OutputRuleGuard


def test_clean_output_passes_unchanged():
    text = "我在听着，您愿意多和我说说吗？"
    result = OutputRuleGuard().run(text)
    assert result.passed is True
    assert result.rewritten is False
    assert result.final_text == text


def test_dosage_like_output_is_rewritten():
    result = OutputRuleGuard().run("您可以吃两片试试。")
    assert result.passed is False
    assert result.rewritten is True
    assert "吃两片" not in result.final_text
    assert "按医嘱" in result.final_text


def test_unit_mention_is_rewritten():
    result = OutputRuleGuard().run("建议加到 500 毫克。")
    assert result.rewritten is True
    assert "毫克" not in result.final_text


def test_emoji_and_child_directed_praise_are_normalized():
    result = OutputRuleGuard().run("您真棒！像个小太阳一样温暖大家 😊")

    assert result.passed is True
    assert result.rewritten is True
    assert "😊" not in result.final_text
    assert "真棒" not in result.final_text
    assert "小太阳" not in result.final_text
    assert "听起来很不错" in result.final_text
    assert "温暖的存在" in result.final_text


def test_guarded_text_is_reflected_in_structured_role_bubbles():
    state = GraphState(
        turn_id="tone_guard_role_bubble",
        user_id="tone_guard_user",
        user_input="今天心情不错",
        mode=CompanionMode.role_first,
        user_profile=UserProfile(user_id="tone_guard_user"),
        draft_reply="同龄共鸣者：您真棒！像个小太阳 😊",
        role_messages=[
            RoleCueMessage(
                role_id=RoleId.same_age_peer,
                role_label="同龄共鸣者",
                text="您真棒！像个小太阳 😊",
            )
        ],
    )

    output_guard_node(
        state,
        SimpleNamespace(output_guard=OutputRuleGuard()),
    )

    assert len(state.role_messages) == 1
    assert state.role_messages[0].text in state.response_text
    assert "真棒" not in state.role_messages[0].text
    assert "小太阳" not in state.role_messages[0].text
    assert "😊" not in state.role_messages[0].text
