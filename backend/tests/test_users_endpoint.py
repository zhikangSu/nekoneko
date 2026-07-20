import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_profile_store
from app.core.config import Settings, get_settings
from app.main import app
from app.stores.profile_store import ProfileStore


@pytest.fixture
def profile_client(tmp_path):
    app.dependency_overrides[get_profile_store] = lambda: ProfileStore(tmp_path)
    app.dependency_overrides[get_settings] = lambda: Settings(
        quiet_hours_start="22:00",
        quiet_hours_end="07:00",
        proactive_max_checkins_per_day=3,
        proactive_same_topic_cooldown_minutes=120,
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_profile_default_for_new_user(profile_client):
    response = profile_client.get("/api/users/demo_user/profile")
    assert response.status_code == 200
    body = response.json()
    assert body["user_id"] == "demo_user"
    assert body["companion_display_name"] is None
    assert body["onboarding_completed"] is False
    assert body["proactive_quiet_hours_start"] is None
    assert body["proactive_quiet_hours_end"] is None
    assert body["proactive_max_checkins_per_day"] is None
    assert body["proactive_same_topic_cooldown_minutes"] is None
    assert body["proactive_effective"] == {
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "07:00",
        "max_checkins_per_day": 3,
        "same_topic_cooldown_minutes": 120,
    }


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


def test_patch_sets_proactive_preferences(profile_client):
    body = profile_client.patch(
        "/api/users/demo_user/profile",
        json={
            "proactive_quiet_hours_start": "21:30",
            "proactive_quiet_hours_end": "06:30",
            "proactive_max_checkins_per_day": 2,
            "proactive_same_topic_cooldown_minutes": 45,
        },
    ).json()
    assert body["proactive_quiet_hours_start"] == "21:30"
    assert body["proactive_quiet_hours_end"] == "06:30"
    assert body["proactive_max_checkins_per_day"] == 2
    assert body["proactive_same_topic_cooldown_minutes"] == 45
    assert body["proactive_effective"] == {
        "quiet_hours_start": "21:30",
        "quiet_hours_end": "06:30",
        "max_checkins_per_day": 2,
        "same_topic_cooldown_minutes": 45,
    }


def test_patch_null_resets_proactive_to_global_default(profile_client):
    profile_client.patch(
        "/api/users/demo_user/profile",
        json={
            "proactive_quiet_hours_start": "21:30",
            "proactive_max_checkins_per_day": 2,
        },
    )
    body = profile_client.patch(
        "/api/users/demo_user/profile",
        json={
            "proactive_quiet_hours_start": None,
            "proactive_max_checkins_per_day": None,
        },
    ).json()

    assert body["proactive_quiet_hours_start"] is None
    assert body["proactive_max_checkins_per_day"] is None
    assert body["proactive_effective"]["quiet_hours_start"] == "22:00"
    assert body["proactive_effective"]["max_checkins_per_day"] == 3
    again = profile_client.get("/api/users/demo_user/profile").json()
    assert again["proactive_max_checkins_per_day"] is None


def test_omitted_proactive_fields_keep_existing_override(profile_client):
    profile_client.patch(
        "/api/users/demo_user/profile",
        json={"proactive_max_checkins_per_day": 2},
    )

    body = profile_client.patch(
        "/api/users/demo_user/profile",
        json={"memory_enabled": False},
    ).json()

    assert body["proactive_max_checkins_per_day"] == 2


def test_effective_values_follow_settings_and_profile_override(profile_client):
    app.dependency_overrides[get_settings] = lambda: Settings(
        quiet_hours_start="21:00",
        quiet_hours_end="08:00",
        proactive_max_checkins_per_day=2,
        proactive_same_topic_cooldown_minutes=60,
    )

    body = profile_client.get("/api/users/env_user/profile").json()
    assert body["proactive_effective"] == {
        "quiet_hours_start": "21:00",
        "quiet_hours_end": "08:00",
        "max_checkins_per_day": 2,
        "same_topic_cooldown_minutes": 60,
    }

    overridden = profile_client.patch(
        "/api/users/env_user/profile",
        json={"proactive_max_checkins_per_day": 1},
    ).json()
    assert overridden["proactive_effective"]["max_checkins_per_day"] == 1
    assert overridden["proactive_effective"]["quiet_hours_start"] == "21:00"


def test_invalid_proactive_preferences_rejected(profile_client):
    bad_time = profile_client.patch(
        "/api/users/demo_user/profile",
        json={"proactive_quiet_hours_start": "25:00"},
    )
    bad_cap = profile_client.patch(
        "/api/users/demo_user/profile",
        json={"proactive_max_checkins_per_day": 7},
    )
    assert bad_time.status_code == 422
    assert bad_cap.status_code == 422


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
