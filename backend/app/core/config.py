"""Application settings, loaded from environment / .env.

The committed ``.env.example`` defaults keep the app fully offline
(``DEMO_MODE=true`` with fake/mock providers), so the demo and tests never call
paid APIs. Reads the repo-root ``.env`` whether the app is launched from the
repo root or from ``backend/``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root = backend/app/core/config.py → parents[3]. Used to resolve relative
# data dirs to one canonical location regardless of the launch CWD.
_REPO_ROOT = Path(__file__).resolve().parents[3]


def _resolve_under_root(path_str: str) -> str:
    path = Path(path_str)
    return str(path if path.is_absolute() else (_REPO_ROOT / path))


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

    # Storage. Relative paths resolve under the repo root (not the launch CWD),
    # so data always lands in <repo>/data/ — the one location that is gitignored.
    profile_dir: str = "./data/profiles"
    trace_log_dir: str = "./data/traces"
    memory_root: str = "./data/memory"
    reminder_dir: str = "./data/reminders"
    guardian_dir: str = "./data/guardian"

    # Proactive care defaults (GuardianAgent, #12)
    proactive_enabled: bool = True
    proactive_max_checkins_per_day: int = 3
    proactive_same_topic_cooldown_minutes: int = 120
    proactive_refusal_pause_hours: int = 24
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"

    # CORS: comma-separated list of allowed frontend origins.
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def resolved_profile_dir(self) -> str:
        return _resolve_under_root(self.profile_dir)

    @property
    def resolved_trace_log_dir(self) -> str:
        return _resolve_under_root(self.trace_log_dir)

    @property
    def resolved_memory_root(self) -> str:
        return _resolve_under_root(self.memory_root)

    @property
    def resolved_reminder_dir(self) -> str:
        return _resolve_under_root(self.reminder_dir)

    @property
    def resolved_guardian_dir(self) -> str:
        return _resolve_under_root(self.guardian_dir)


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor used as a FastAPI dependency."""
    return Settings()
