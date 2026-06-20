"""Request/response models for the voice endpoints (issue #4).

``POST /api/voice/asr`` takes the recorded audio as the raw request body (no
multipart dependency) and returns a transcript; ``ok=false`` means nothing was
recognized, so the UI shows a gentle retry prompt and keeps the text path.

``POST /api/voice/tts`` takes reply text and returns base64-encoded audio so the
frontend can play and replay it. ``is_mock`` lets the UI label the placeholder
voice in DEMO_MODE.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ASRResponse(BaseModel):
    transcript: str
    confidence: float
    # False when nothing was recognized (empty / too-short audio).
    ok: bool
    provider: str
    is_mock: bool


class TTSRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    voice: Optional[str] = None

    @field_validator("text")
    @classmethod
    def _text_not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("text must not be blank")
        return stripped


class TTSResponse(BaseModel):
    audio_base64: str
    content_type: str
    provider: str
    voice: str
    # True when this exact text was synthesized before (served from cache).
    cached: bool
    is_mock: bool
