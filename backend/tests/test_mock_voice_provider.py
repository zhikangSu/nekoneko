"""MockASRProvider / MockTTSProvider: deterministic, offline, playable (#4)."""

import io
import wave

from app.services.mock_voice_provider import MockASRProvider, MockTTSProvider


def _wav_frames(audio: bytes) -> int:
    with wave.open(io.BytesIO(audio), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == 16_000
        return wav.getnframes()


def test_mock_asr_returns_deterministic_nonempty_transcript():
    asr = MockASRProvider()
    audio = b"\x01" * 4096
    first = asr.transcribe(audio)
    second = asr.transcribe(audio)
    assert first.transcript == second.transcript
    assert first.transcript.strip()
    assert 0.0 < first.confidence <= 1.0
    assert first.provider == "mock"


def test_mock_asr_empty_or_tiny_audio_is_blank():
    asr = MockASRProvider()
    assert asr.transcribe(b"").transcript == ""
    assert asr.transcribe(b"").confidence == 0.0
    # A handful of bytes is treated as "nothing was said".
    assert asr.transcribe(b"\x00" * 8).transcript == ""


def test_mock_tts_returns_valid_playable_wav():
    result = MockTTSProvider().synthesize("今天天气不错")
    assert result.content_type == "audio/wav"
    assert result.provider == "mock"
    assert _wav_frames(result.audio) > 0


def test_mock_tts_is_deterministic():
    a = MockTTSProvider().synthesize("你好呀")
    b = MockTTSProvider().synthesize("你好呀")
    assert a.audio == b.audio


def test_mock_tts_duration_scales_with_text_length():
    short = MockTTSProvider().synthesize("好")
    long = MockTTSProvider().synthesize("今天想出门散步晒晒太阳再买点菜回来做饭")
    assert _wav_frames(long.audio) > _wav_frames(short.audio)
