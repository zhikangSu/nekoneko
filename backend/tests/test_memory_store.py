import pytest

from app.schemas.memory import MemoryCategory
from app.stores.memory_store import MemoryStore


def test_add_and_list(tmp_path):
    store = MemoryStore(tmp_path)
    entry = store.add("demo_user", MemoryCategory.profile_preference, "喜欢粤剧")
    assert entry.id.startswith("m_")
    items = store.list("demo_user")
    assert [m.content for m in items] == ["喜欢粤剧"]


def test_markdown_is_rendered(tmp_path):
    store = MemoryStore(tmp_path)
    store.add("demo_user", MemoryCategory.profile_preference, "喜欢粤剧")
    md = (tmp_path / "users" / "demo_user" / "memory.md").read_text(encoding="utf-8")
    assert "喜欢粤剧" in md
    assert "偏好" in md


def test_add_if_absent_dedupes(tmp_path):
    store = MemoryStore(tmp_path)
    store.add_if_absent("u", MemoryCategory.profile_preference, "喜欢粤剧")
    dup = store.add_if_absent("u", MemoryCategory.profile_preference, "喜欢粤剧")
    assert dup is None
    assert len(store.list("u")) == 1


def test_delete(tmp_path):
    store = MemoryStore(tmp_path)
    entry = store.add("u", MemoryCategory.event_memory, "孙女周日来访")
    assert store.delete("u", entry.id) is True
    assert store.list("u") == []
    assert store.delete("u", "missing") is False


def test_pause_extraction(tmp_path):
    store = MemoryStore(tmp_path)
    assert store.is_extraction_paused("u") is False
    store.set_extraction_paused("u", True)
    assert store.is_extraction_paused("u") is True


def test_invalid_user_id(tmp_path):
    with pytest.raises(ValueError):
        MemoryStore(tmp_path).list("bad.id")
