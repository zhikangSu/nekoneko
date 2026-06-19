"""Application settings, loaded from environment / .env.

The committed ``.env.example`` defaults keep the app fully offline
(``DEMO_MODE=true`` with fake/mock providers), so the demo and tests never call
paid APIs. Reads the repo-root ``.env`` whether the app is launched from the
repo root or from ``backend/``.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Look for .env in the current dir (backend/) and the repo root (../).
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Runtime
    app_env: str = "development"
    demo_mode: bool = True
    log_level: str = "info"

    # Providers (fake/mock by default)
    llm_provider: str = "fake"
    asr_provider: str = "mock"
    tts_provider: str = "mock"
    retrieval_provider: str = "mock"

    # API keys (empty in committed file; never hardcode secrets)
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Budget controls
    max_llm_calls_per_turn: int = 2
    max_web_calls_per_turn: int = 1

    # Storage
    profile_dir: str = "./data/profiles"
    trace_log_dir: str = "./data/traces"

    # CORS: comma-separated list of allowed frontend origins.
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor used as a FastAPI dependency."""
    return Settings()
