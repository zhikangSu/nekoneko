import pytest

from app.core.config import Settings
from app.core.constants import CompanionMode
from app.services.fake_llm_provider import FakeLLMProvider
from app.services.llm_provider import CompanionReplyInput, get_llm_provider
from app.services.xiaomimimo_llm_provider import XiaomiMiMoLLMProvider


def test_fake_provider_selected_for_fake():
    settings = Settings(llm_provider="fake", demo_mode=True)
    assert isinstance(get_llm_provider(settings), FakeLLMProvider)


def test_demo_mode_falls_back_to_fake_for_unimplemented_provider():
    # "DEMO_MODE provider fallback": an unimplemented provider name must not
    # break the demo when DEMO_MODE=true.
    settings = Settings(llm_provider="openai", demo_mode=True)
    assert isinstance(get_llm_provider(settings), FakeLLMProvider)


def test_demo_mode_uses_fake_even_with_real_provider_named():
    # DEMO_MODE must never need a key, even if a real provider is named.
    settings = Settings(llm_provider="xiaomimimo", demo_mode=True, openai_api_key="k")
    assert isinstance(get_llm_provider(settings), FakeLLMProvider)


def test_real_provider_selected_when_configured():
    # Constructed, not invoked — no live call.
    settings = Settings(llm_provider="xiaomimimo", demo_mode=False, openai_api_key="k")
    assert isinstance(get_llm_provider(settings), XiaomiMiMoLLMProvider)


def test_real_provider_requires_api_key():
    settings = Settings(llm_provider="xiaomimimo", demo_mode=False, openai_api_key="")
    with pytest.raises(RuntimeError):
        get_llm_provider(settings)


def test_non_demo_unimplemented_provider_raises():
    settings = Settings(llm_provider="openai", demo_mode=False, openai_api_key="k")
    with pytest.raises(RuntimeError):
        get_llm_provider(settings)


def test_fake_reply_is_deterministic_and_mode_aware():
    provider = FakeLLMProvider()
    role = provider.generate_companion_reply(
        CompanionReplyInput("我有点累", CompanionMode.role_first, "陪伴 AI")
    )
    role_again = provider.generate_companion_reply(
        CompanionReplyInput("我有点累", CompanionMode.role_first, "陪伴 AI")
    )
    neutral = provider.generate_companion_reply(
        CompanionReplyInput("我有点累", CompanionMode.neutral_assistant, "陪伴 AI")
    )
    assert role == role_again  # deterministic
    assert role and neutral
    assert "？" not in role and "?" not in role
    assert "？" not in neutral and "?" not in neutral


def test_fake_provider_generation_info_is_trace_safe():
    provider = FakeLLMProvider()
    provider.generate_companion_reply(
        CompanionReplyInput("你好", CompanionMode.role_first, "陪伴 AI")
    )
    assert provider.generation_info == {"provider": "fake", "used_fallback": False}


def test_real_provider_marks_fallback_when_api_call_fails(monkeypatch):
    provider = XiaomiMiMoLLMProvider(
        Settings(llm_provider="xiaomimimo", demo_mode=False, openai_api_key="k")
    )

    def fail(_body):
        raise TimeoutError("simulated timeout")

    monkeypatch.setattr(provider, "_post", fail)

    text = provider.generate_companion_reply(
        CompanionReplyInput("我有点累", CompanionMode.role_first, "陪伴 AI")
    )

    assert text
    assert provider.generation_info["provider"] == "xiaomimimo"
    assert provider.generation_info["used_fallback"] is True
    assert provider.generation_info["fallback_provider"] == "fake"
    assert provider.generation_info["error_type"] == "TimeoutError"
