"""Shared test fixtures.

Force offline/fake providers before the app is imported so tests never call
real LLM / ASR / TTS / web APIs, regardless of any local ``.env``.
"""

from __future__ import annotations

import os
import tempfile

os.environ["DEMO_MODE"] = "true"
os.environ["LLM_PROVIDER"] = "fake"
os.environ["ASR_PROVIDER"] = "mock"
os.environ["TTS_PROVIDER"] = "mock"
# Never let a real API key from the repo-root .env reach the test suite, so a
# real ASR/TTS/LLM provider can never be exercised live (CLAUDE.md §12).
os.environ["OPENAI_API_KEY"] = ""
# Point the default stores at throwaway dirs so tests never write to the repo's
# data/. (Endpoint tests that assert persistence override the store per-test.)
os.environ["PROFILE_DIR"] = tempfile.mkdtemp(prefix="qaq_test_profiles_")
os.environ["TRACE_LOG_DIR"] = tempfile.mkdtemp(prefix="qaq_test_traces_")
os.environ["MEMORY_ROOT"] = tempfile.mkdtemp(prefix="qaq_test_memory_")
os.environ["MEMORY_CARDS_DIR"] = tempfile.mkdtemp(prefix="qaq_test_memory_cards_")
os.environ["REMINDER_DIR"] = tempfile.mkdtemp(prefix="qaq_test_reminders_")
os.environ["GUARDIAN_DIR"] = tempfile.mkdtemp(prefix="qaq_test_guardian_")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
