from fastapi.testclient import TestClient

from app.agents.companion import CompanionAgent
from app.api.deps import get_profile_store
from app.core.constants import DEFAULT_COMPANION_DISPLAY_NAME, CompanionMode
from app.main import app
from app.schemas.profile import ProfileUpdate
from app.services.fake_llm_provider import FakeLLMProvider
from app.stores.profile_store import ProfileStore


def _agent() -> CompanionAgent:
    return CompanionAgent(FakeLLMProvider())


def test_role_first_uses_user_name_in_prompt():
    result = _agent().respond(
        message="我今天有点想老伴了。",
        mode=CompanionMode.role_first,
        companion_display_name="阿南",
    )
    assert result.named_by_user is True
    assert result.companion_display_name == "阿南"
    assert "阿南" in result.rendered_prompt
    assert "{companion_display_name}" not in result.rendered_prompt
    assert result.reply_text.strip()


def test_unnamed_falls_back_without_hardcoded_name():
    result = _agent().respond(
        message="你好",
        mode=CompanionMode.role_first,
        companion_display_name=None,
    )
    assert result.named_by_user is False
    assert result.companion_display_name == DEFAULT_COMPANION_DISPLAY_NAME
    assert DEFAULT_COMPANION_DISPLAY_NAME in result.rendered_prompt


def test_blank_name_is_treated_as_unnamed():
    result = _agent().respond(
        message="你好", mode=CompanionMode.role_first, companion_display_name="   "
    )
    assert result.named_by_user is False
    assert result.companion_display_name == DEFAULT_COMPANION_DISPLAY_NAME


def test_modes_select_different_prompts():
    role = _agent().respond(
        message="你好", mode=CompanionMode.role_first, companion_display_name=None
    )
    neutral = _agent().respond(
        message="你好", mode=CompanionMode.neutral_assistant, companion_display_name=None
    )
    assert "role-first order" in role.rendered_prompt
    assert "comparison condition" in neutral.rendered_prompt
    assert role.trace_summary() != neutral.trace_summary()


def test_manual_role_style_context_is_added_to_prompt():
    result = _agent().respond(
        message="我终于也是活到了我妈妈的那个年纪",
        mode=CompanionMode.role_first,
        companion_display_name=None,
        role_style_context="elder_mentor / 长辈引导者：温厚、包容，先安抚再反思。",
    )

    assert "关系角色口吻" in result.rendered_prompt
    assert "长辈引导者" in result.rendered_prompt
    assert "不要退回默认的“陪伴 AI”泛化口吻" in result.rendered_prompt


def test_reply_is_deterministic():
    a = _agent().respond(
        message="我有点累", mode=CompanionMode.role_first, companion_display_name="阿南"
    )
    b = _agent().respond(
        message="我有点累", mode=CompanionMode.role_first, companion_display_name="阿南"
    )
    assert a.reply_text == b.reply_text


def test_chat_endpoint_uses_profile_name(tmp_path):
    store = ProfileStore(tmp_path)
    store.update(
        "demo_user",
        ProfileUpdate(companion_display_name="小南", onboarding_completed=True),
    )
    app.dependency_overrides[get_profile_store] = lambda: store
    try:
        client = TestClient(app)
        body = client.post(
            "/api/chat",
            json={
                "user_id": "demo_user",
                "message": "我今天有点想老伴了。",
                "mode": "role_first",
            },
        ).json()
        agents = body["agent_trace"]["agents"]
        step = next(s for s in agents if s["name"] == "CompanionAgent")
        assert step["detail"]["companion_display_name"] == "小南"
        assert step["detail"]["named_by_user"] is True
    finally:
        app.dependency_overrides.clear()
