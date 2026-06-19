import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_profile_store
from app.main import app
from app.stores.profile_store import ProfileStore


@pytest.fixture
def profile_client(tmp_path):
    app.dependency_overrides[get_profile_store] = lambda: ProfileStore(tmp_path)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_profile_default_for_new_user(profile_client):
    response = profile_client.get("/api/users/demo_user/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "demo_user"
    assert body["companion_display_name"] is None
    assert body["onboarding_completed"] is False


def test_patch_sets_companion_name(profile_client):
    response = profile_client.patch(
        "/api/users/demo_user/profile",
        json={"companion_display_name": "小南", "onboarding_completed": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["companion_display_name"] == "小南"
    assert body["onboarding_completed"] is True
    # Persisted across requests.
    again = profile_client.get("/api/users/demo_user/profile").json()
    assert again["companion_display_name"] == "小南"


def test_patch_clears_name_back_to_fallback(profile_client):
    profile_client.patch(
        "/api/users/demo_user/profile", json={"companion_display_name": "小南"}
    )
    cleared = profile_client.patch(
        "/api/users/demo_user/profile", json={"companion_display_name": ""}
    ).json()
    assert cleared["companion_display_name"] is None


def test_patch_toggles_preferences(profile_client):
    body = profile_client.patch(
        "/api/users/demo_user/profile",
        json={"memory_enabled": False, "proactive_checkin_enabled": False},
    ).json()
    assert body["memory_enabled"] is False
    assert body["proactive_checkin_enabled"] is False


def test_skip_onboarding_keeps_name_empty(profile_client):
    # "Skip" = complete onboarding without choosing a name.
    body = profile_client.patch(
        "/api/users/demo_user/profile", json={"onboarding_completed": True}
    ).json()
    assert body["onboarding_completed"] is True
    assert body["companion_display_name"] is None


def test_name_too_long_rejected(profile_client):
    response = profile_client.patch(
        "/api/users/demo_user/profile",
        json={"companion_display_name": "名" * 41},
    )
    assert response.status_code == 422


def test_invalid_user_id_rejected(profile_client):
    assert profile_client.get("/api/users/bad.id/profile").status_code == 422
