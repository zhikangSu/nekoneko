import pytest

from app.core.config import Settings
from app.core.constants import CompanionMode
from app.services.fake_llm_provider import FakeLLMProvider
from app.services.llm_provider import CompanionReplyInput, get_llm_provider


def test_fake_provider_selected_for_fake():
    settings = Settings(llm_provider="fake", demo_mode=True)
    assert isinstance(get_llm_provider(settings), FakeLLMProvider)


def test_demo_mode_falls_back_to_fake_for_unimplemented_provider():
    # "DEMO_MODE provider fallback": an unimplemented provider name must not
    # break the demo when DEMO_MODE=true.
    settings = Settings(llm_provider="openai", demo_mode=True)
    assert isinstance(get_llm_provider(settings), FakeLLMProvider)


def test_non_demo_unimplemented_provider_raises():
    settings = Settings(llm_provider="openai", demo_mode=False)
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
