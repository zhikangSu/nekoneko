"""Shared test fixtures.

Force offline/fake providers before the app is imported so tests never call
real LLM / ASR / TTS / web APIs, regardless of any local ``.env``.
"""

from __future__ import annotations

import os
import tempfile

os.environ["DEMO_MODE"] = "true"
os.environ["LLM_PROVIDER"] = "fake"
# Point the default profile store at a throwaway dir so tests never write to the
# repo's data/profiles. (Profile-endpoint tests override the store per-test.)
os.environ["PROFILE_DIR"] = tempfile.mkdtemp(prefix="qaq_test_profiles_")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
