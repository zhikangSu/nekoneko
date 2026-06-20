"""/api/voice/asr + /api/voice/tts endpoint behavior (#4)."""

import base64
import io
import wave

from app.core.config import Settings, get_settings
from app.main import app
from app.services.voice_provider import tts_cache


def test_asr_endpoint_transcribes_audio(client):
    response = client.post(
        "/api/voice/asr",
        content=b"\x01" * 4096,
        headers={"content-type": "audio/webm"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["transcript"].strip()
    assert body["is_mock"] is True
    assert body["provider"] == "mock"


def test_asr_endpoint_blank_on_empty_audio(client):
    response = client.post("/api/voice/asr", content=b"")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["transcript"] == ""


def test_asr_endpoint_rejects_oversized_audio(client):
    app.dependency_overrides[get_settings] = lambda: Settings(max_voice_upload_bytes=16)
    try:
        response = client.post("/api/voice/asr", content=b"x" * 64)
        assert response.status_code == 413
    finally:
        app.dependency_overrides.clear()


def test_tts_endpoint_returns_playable_wav(client):
    tts_cache.clear()
    response = client.post("/api/voice/tts", json={"text": "今天天气不错"})
    assert response.status_code == 200
    body = response.json()
    assert body["cached"] is False
    assert body["is_mock"] is True
    audio = base64.b64decode(body["audio_base64"])
    with wave.open(io.BytesIO(audio), "rb") as wav:
        assert wav.getnframes() > 0


def test_tts_endpoint_caches_repeat_text(client):
    tts_cache.clear()
    first = client.post("/api/voice/tts", json={"text": "重播这一句"}).json()
    second = client.post("/api/voice/tts", json={"text": "重播这一句"}).json()
    assert first["cached"] is False
    assert second["cached"] is True
    # Replay serves identical audio without re-synthesizing.
    assert first["audio_base64"] == second["audio_base64"]


def test_tts_endpoint_rejects_blank_text(client):
    assert client.post("/api/voice/tts", json={"text": "   "}).status_code == 422
    assert client.post("/api/voice/tts", json={"text": ""}).status_code == 422
