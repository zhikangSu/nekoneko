import json

import pytest

from app.schemas.profile import ProfileUpdate
from app.stores.profile_store import ProfileStore


def test_get_returns_default_without_persisting(tmp_path):
    store = ProfileStore(tmp_path)
    profile = store.get("demo_user")
    assert profile.user_id == "demo_user"
    assert profile.companion_display_name is None
    assert profile.onboarding_completed is False
    assert profile.memory_enabled is True
    assert profile.proactive_checkin_enabled is True
    assert profile.proactive_quiet_hours_start is None
    assert profile.proactive_quiet_hours_end is None
    assert profile.proactive_max_checkins_per_day is None
    assert profile.proactive_same_topic_cooldown_minutes is None
    # GET must not write a file.
    assert not (tmp_path / "demo_user.json").exists()


def test_update_sets_and_persists(tmp_path):
    store = ProfileStore(tmp_path)
    updated = store.update(
        "demo_user",
        ProfileUpdate(companion_display_name="小南", onboarding_completed=True),
    )
    assert updated.companion_display_name == "小南"
    assert updated.onboarding_completed is True
    # A second store instance reads the persisted value.
    assert ProfileStore(tmp_path).get("demo_user").companion_display_name == "小南"


def test_update_only_changes_provided_fields(tmp_path):
    store = ProfileStore(tmp_path)
    store.update("demo_user", ProfileUpdate(companion_display_name="小南"))
    store.update(
        "demo_user",
        ProfileUpdate(memory_enabled=False, proactive_max_checkins_per_day=2),
    )
    profile = store.get("demo_user")
    assert profile.companion_display_name == "小南"  # untouched
    assert profile.memory_enabled is False
    assert profile.proactive_max_checkins_per_day == 2


def test_explicit_null_resets_proactive_override(tmp_path):
    store = ProfileStore(tmp_path)
    store.update("demo_user", ProfileUpdate(proactive_max_checkins_per_day=2))

    reset = store.update(
        "demo_user",
        ProfileUpdate.model_validate({"proactive_max_checkins_per_day": None}),
    )

    assert reset.proactive_max_checkins_per_day is None


def test_legacy_built_in_values_migrate_to_unset(tmp_path):
    path = tmp_path / "demo_user.json"
    path.write_text(
        json.dumps(
            {
                "user_id": "demo_user",
                "companion_display_name": "小南",
                "proactive_quiet_hours_start": "22:00",
                "proactive_quiet_hours_end": "07:00",
                "proactive_max_checkins_per_day": 3,
                "proactive_same_topic_cooldown_minutes": 120,
            }
        ),
        encoding="utf-8",
    )

    profile = ProfileStore(tmp_path).get("demo_user")

    assert profile.companion_display_name == "小南"
    assert profile.proactive_quiet_hours_start is None
    assert profile.proactive_quiet_hours_end is None
    assert profile.proactive_max_checkins_per_day is None
    assert profile.proactive_same_topic_cooldown_minutes is None


def test_legacy_custom_values_remain_overrides(tmp_path):
    path = tmp_path / "demo_user.json"
    path.write_text(
        json.dumps(
            {
                "user_id": "demo_user",
                "proactive_quiet_hours_start": "21:30",
                "proactive_quiet_hours_end": "06:30",
                "proactive_max_checkins_per_day": 2,
                "proactive_same_topic_cooldown_minutes": 45,
            }
        ),
        encoding="utf-8",
    )

    profile = ProfileStore(tmp_path).get("demo_user")

    assert profile.proactive_quiet_hours_start == "21:30"
    assert profile.proactive_quiet_hours_end == "06:30"
    assert profile.proactive_max_checkins_per_day == 2
    assert profile.proactive_same_topic_cooldown_minutes == 45


def test_new_format_marker_preserves_deliberate_default_value_override(tmp_path):
    store = ProfileStore(tmp_path)
    store.update("demo_user", ProfileUpdate(proactive_max_checkins_per_day=3))

    raw = json.loads((tmp_path / "demo_user.json").read_text(encoding="utf-8"))
    assert raw["_proactive_overrides_initialized"] is True
    assert ProfileStore(tmp_path).get(
        "demo_user"
    ).proactive_max_checkins_per_day == 3


def test_clear_name_with_blank(tmp_path):
    store = ProfileStore(tmp_path)
    store.update("demo_user", ProfileUpdate(companion_display_name="小南"))
    cleared = store.update("demo_user", ProfileUpdate(companion_display_name="  "))
    assert cleared.companion_display_name is None


def test_name_is_trimmed(tmp_path):
    store = ProfileStore(tmp_path)
    updated = store.update("demo_user", ProfileUpdate(companion_display_name="  阿福 "))
    assert updated.companion_display_name == "阿福"


def test_invalid_user_id_raises(tmp_path):
    store = ProfileStore(tmp_path)
    with pytest.raises(ValueError):
        store.get("bad.id")
