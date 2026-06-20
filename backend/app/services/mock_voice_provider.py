"""Deterministic, offline ASR/TTS mocks (DEMO_MODE default, issue #4).

These let the whole voice loop run with no microphone model and no paid speech
API, so the demo and tests work offline:

* ``MockASRProvider`` cannot really transcribe audio offline, so it returns a
  **simulated** transcript chosen deterministically from the clip length. The
  text is a natural companion-style utterance so the downstream chat reply still
  makes sense in a demo. Empty / too-short audio yields an empty transcript so
  the UI shows the gentle "I didn't catch that" prompt.
* ``MockTTSProvider`` synthesizes a short, soft sine-tone WAV with the Python
  standard library (no dependencies). It is a *placeholder voice* — real speech
  arrives with #23 — but it is genuine, playable, replayable audio, so the
  frontend audio path is exercised for real.
"""

from __future__ import annotations

import io
import math
import struct
import wave
from typing import Optional

from app.services.voice_provider import ASRProvider, ASRResult, TTSProvider, TTSResult

# Below this many bytes we treat the clip as "nothing was said".
_MIN_AUDIO_BYTES = 64

# Simulated transcripts (demo only). Warm, everyday utterances that route to a
# sensible companion reply; deliberately not medical/dosage content.
_MOCK_TRANSCRIPTS = (
    "今天天气怎么样，要不要出门走走？",
    "我有点想孩子了，好久没和他们说话。",
    "帮我记一下，下午三点要量血压。",
    "我昨晚没睡好，今天有点累。",
    "陪我聊聊吧，家里今天挺安静的。",
)


class MockASRProvider(ASRProvider):
    name = "mock"

    def transcribe(
        self, audio: bytes, *, content_type: Optional[str] = None
    ) -> ASRResult:
        if not audio or len(audio) < _MIN_AUDIO_BYTES:
            return ASRResult(transcript="", confidence=0.0, provider=self.name)
        # Deterministic pick (no randomness): stable per clip length.
        index = len(audio) % len(_MOCK_TRANSCRIPTS)
        return ASRResult(
            transcript=_MOCK_TRANSCRIPTS[index],
            confidence=0.92,
            provider=self.name,
        )


# WAV synthesis parameters. A soft, low tone whose length tracks the reply
# length — short enough not to drone, just enough to prove play/replay.
_SAMPLE_RATE = 16_000
_TONE_HZ = 220.0
_AMPLITUDE = 0.16
_MIN_SECONDS = 0.5
_MAX_SECONDS = 2.5
_SECONDS_PER_CHAR = 0.12
_FADE_SECONDS = 0.05  # fade in/out to avoid clicks


def _render_tone_wav(seconds: float) -> bytes:
    """Render a mono 16-bit PCM WAV of a faded sine tone."""
    frame_count = int(_SAMPLE_RATE * seconds)
    fade = max(1, int(_SAMPLE_RATE * _FADE_SECONDS))
    frames = bytearray()
    for i in range(frame_count):
        envelope = min(1.0, i / fade, (frame_count - i) / fade)
        sample = int(
            _AMPLITUDE * envelope * 32767 * math.sin(2 * math.pi * _TONE_HZ * i / _SAMPLE_RATE)
        )
        frames += struct.pack("<h", sample)

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(_SAMPLE_RATE)
        wav.writeframes(bytes(frames))
    return buffer.getvalue()


class MockTTSProvider(TTSProvider):
    name = "mock"

    def synthesize(self, text: str, *, voice: Optional[str] = None) -> TTSResult:
        length = len((text or "").strip())
        seconds = max(_MIN_SECONDS, min(_MAX_SECONDS, length * _SECONDS_PER_CHAR))
        return TTSResult(
            audio=_render_tone_wav(seconds),
            content_type="audio/wav",
            provider=self.name,
            voice=voice or "",
        )
