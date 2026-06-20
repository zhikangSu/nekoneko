"""Voice I/O endpoints — mock ASR / TTS for the offline demo (issue #4).

    POST /api/voice/asr   raw audio body  → transcript
    POST /api/voice/tts   {text, voice?}  → base64 audio (cached on repeat)

Both run behind the provider interfaces in ``services/voice_provider`` so #23 can
swap in a real ASR/TTS provider without touching this layer. In DEMO_MODE the
providers are deterministic mocks: no microphone model, no paid speech API.
"""

from __future__ import annotations

import base64

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.config import Settings, get_settings
from app.schemas.voice import ASRResponse, TTSRequest, TTSResponse
from app.services.voice_provider import (
    MOCK_PROVIDER_NAMES,
    get_asr_provider,
    get_tts_provider,
    synthesize_cached,
)

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/asr", response_model=ASRResponse)
async def transcribe(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> ASRResponse:
    audio = await request.body()
    if len(audio) > settings.max_voice_upload_bytes:
        raise HTTPException(status_code=413, detail="audio payload too large")

    provider = get_asr_provider(settings)
    result = provider.transcribe(
        audio, content_type=request.headers.get("content-type")
    )
    return ASRResponse(
        transcript=result.transcript,
        confidence=result.confidence,
        ok=bool(result.transcript.strip()),
        provider=result.provider,
        is_mock=result.provider in MOCK_PROVIDER_NAMES,
    )


@router.post("/tts", response_model=TTSResponse)
def synthesize(
    request: TTSRequest,
    settings: Settings = Depends(get_settings),
) -> TTSResponse:
    provider = get_tts_provider(settings)
    result = synthesize_cached(provider, request.text, voice=request.voice)
    return TTSResponse(
        audio_base64=base64.b64encode(result.audio).decode("ascii"),
        content_type=result.content_type,
        provider=result.provider,
        voice=result.voice,
        cached=result.cached,
        is_mock=result.provider in MOCK_PROVIDER_NAMES,
    )
