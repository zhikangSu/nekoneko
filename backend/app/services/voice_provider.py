"""ASR / TTS provider interfaces, selection, and a small TTS cache (issues #4, #23).

Voice I/O sits behind these interfaces so the demo runs fully offline in
``DEMO_MODE=true`` with deterministic mock providers (AGENTS.md §7) — no
microphone model and no paid speech API. Issue #4 ships the mock providers; #23
adds a real ASR/TTS provider behind the same contract, keeping the mock fallback
so a live-API outage never breaks the demo.

``transcribe`` never raises on empty/too-short audio — it returns an empty
transcript so the caller can show a gentle "I didn't catch that" prompt and keep
the text path working (FR-01 fallback).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, replace
from typing import Optional

from app.core.config import Settings

logger = logging.getLogger(__name__)

# Provider names that mean "use the offline mock" (kept in sync with config).
MOCK_PROVIDER_NAMES = {"mock", "fake"}


@dataclass
class ASRResult:
    """Outcome of transcribing one audio clip.

    An empty ``transcript`` with ``confidence == 0`` signals "nothing
    recognized" — the caller shows a gentle retry prompt rather than an error.
    """

    transcript: str
    confidence: float
    provider: str = "mock"
    is_final: bool = True


@dataclass
class TTSResult:
    """Synthesized audio for one reply. ``cached`` is set by ``synthesize_cached``."""

    audio: bytes
    content_type: str
    provider: str = "mock"
    voice: str = ""
    cached: bool = False


class ASRProvider(ABC):
    name: str = "base"

    @abstractmethod
    def transcribe(
        self, audio: bytes, *, content_type: Optional[str] = None
    ) -> ASRResult:
        """Transcribe spoken audio to text. Must not raise on empty audio."""


class TTSProvider(ABC):
    name: str = "base"

    @abstractmethod
    def synthesize(self, text: str, *, voice: Optional[str] = None) -> TTSResult:
        """Synthesize speech audio for ``text``."""


def get_asr_provider(settings: Settings) -> ASRProvider:
    """Select an ASR provider, with a demo-mode fallback to the mock."""
    # Imported here to avoid a circular import at module load.
    from app.services.mock_voice_provider import MockASRProvider

    provider = (settings.asr_provider or "").strip().lower()
    if provider in MOCK_PROVIDER_NAMES:
        return MockASRProvider()
    if settings.demo_mode:
        logger.warning(
            "ASR_PROVIDER=%r is not implemented yet; falling back to the mock "
            "provider because DEMO_MODE=true.",
            provider,
        )
        return MockASRProvider()
    raise RuntimeError(
        f"ASR provider {provider!r} is not available. Issue #4 only implements "
        "the mock provider (real provider arrives with #23). Set ASR_PROVIDER=mock "
        "or DEMO_MODE=true."
    )


def get_tts_provider(settings: Settings) -> TTSProvider:
    """Select a TTS provider, with a demo-mode fallback to the mock."""
    from app.services.mock_voice_provider import MockTTSProvider

    provider = (settings.tts_provider or "").strip().lower()
    if provider in MOCK_PROVIDER_NAMES:
        return MockTTSProvider()
    if settings.demo_mode:
        logger.warning(
            "TTS_PROVIDER=%r is not implemented yet; falling back to the mock "
            "provider because DEMO_MODE=true.",
            provider,
        )
        return MockTTSProvider()
    raise RuntimeError(
        f"TTS provider {provider!r} is not available. Issue #4 only implements "
        "the mock provider (real provider arrives with #23). Set TTS_PROVIDER=mock "
        "or DEMO_MODE=true."
    )


class _TTSCache:
    """Tiny in-memory LRU for synthesized replies.

    Provider-agnostic so the real provider (#23) reuses it — the point of the
    cache is to avoid re-synthesizing (and, for a paid provider, re-paying for)
    the same reply on replay. Process-local and bounded; fine for a single-user
    demo, not a durable store.
    """

    def __init__(self, max_entries: int = 64) -> None:
        self._store: "OrderedDict[tuple[str, str, str], TTSResult]" = OrderedDict()
        self._max = max_entries

    def get(self, key: tuple[str, str, str]) -> Optional[TTSResult]:
        result = self._store.get(key)
        if result is not None:
            self._store.move_to_end(key)
        return result

    def put(self, key: tuple[str, str, str], value: TTSResult) -> None:
        self._store[key] = value
        self._store.move_to_end(key)
        while len(self._store) > self._max:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()


# Process-wide cache shared across requests (tests call ``tts_cache.clear()``).
tts_cache = _TTSCache()


def synthesize_cached(
    provider: TTSProvider, text: str, *, voice: Optional[str] = None
) -> TTSResult:
    """Synthesize ``text``, returning a cached result on repeat (``cached=True``)."""
    key = (provider.name, voice or "", text)
    hit = tts_cache.get(key)
    if hit is not None:
        return replace(hit, cached=True)
    result = provider.synthesize(text, voice=voice)
    tts_cache.put(key, result)
    return result
