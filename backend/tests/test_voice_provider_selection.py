"""Provider selection: mock by name, mock fallback in DEMO_MODE, else raise (#4)."""

import pytest

from app.core.config import Settings
from app.services.voice_provider import get_asr_provider, get_tts_provider


def test_mock_selected_when_named():
    assert get_asr_provider(Settings(asr_provider="mock")).name == "mock"
    assert get_tts_provider(Settings(tts_provider="mock")).name == "mock"


def test_demo_mode_falls_back_to_mock():
    # An unimplemented real provider name still works offline in DEMO_MODE.
    asr = get_asr_provider(Settings(asr_provider="xiaomimimo", demo_mode=True))
    tts = get_tts_provider(Settings(tts_provider="xiaomimimo", demo_mode=True))
    assert asr.name == "mock"
    assert tts.name == "mock"


def test_unimplemented_provider_without_demo_mode_raises():
    with pytest.raises(RuntimeError):
        get_asr_provider(Settings(asr_provider="xiaomimimo", demo_mode=False))
    with pytest.raises(RuntimeError):
        get_tts_provider(Settings(tts_provider="xiaomimimo", demo_mode=False))
