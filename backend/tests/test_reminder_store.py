import pytest

from app.schemas.reminder import Recurrence
from app.stores.reminder_store import ReminderStore


def test_add_list_get(tmp_path):
    store = ReminderStore(tmp_path)
    reminder = store.add("u", content="吃药", time="08:00", recurrence=Recurrence.daily)
    assert reminder.id.startswith("r_")
    assert len(store.list("u")) == 1
    assert store.get("u", reminder.id).content == "吃药"


def test_delete(tmp_path):
    store = ReminderStore(tmp_path)
    reminder = store.add("u", content="喝水", time="10:00", recurrence=Recurrence.daily)
    assert store.delete("u", reminder.id) is True
    assert store.list("u") == []
    assert store.delete("u", "missing") is False


def test_confirm_sets_timestamp(tmp_path):
    store = ReminderStore(tmp_path)
    reminder = store.add("u", content="吃药", time="08:00", recurrence=Recurrence.daily)
    updated = store.confirm("u", reminder.id)
    assert updated is not None
    assert updated.last_confirmed_at is not None


def test_invalid_user_id(tmp_path):
    with pytest.raises(ValueError):
        ReminderStore(tmp_path).list("bad.id")
