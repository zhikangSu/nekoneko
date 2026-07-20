from app.schemas.memory import MemoryCategory
from app.stores.memory_store import MemoryStore
from app.tools.memory_tool import MemoryTool


def _tool(tmp_path) -> MemoryTool:
    return MemoryTool(MemoryStore(tmp_path))


def test_extract_preferences(tmp_path):
    tool = _tool(tmp_path)
    assert tool.extract_preferences("我喜欢听粤剧") == ["喜欢听粤剧"]
    assert tool.extract_preferences("我喜欢粤剧，每天都听") == ["喜欢粤剧"]
    assert tool.extract_preferences("今天天气不错") == []


def test_remember_from_text_saves_once(tmp_path):
    tool = _tool(tmp_path)
    saved = tool.remember_from_text("u", "我喜欢听粤剧")
    assert [m.content for m in saved] == ["喜欢听粤剧"]
    # second time is a no-op (dedup)
    assert tool.remember_from_text("u", "我喜欢听粤剧") == []


def test_remember_skips_when_paused(tmp_path):
    store = MemoryStore(tmp_path)
    store.set_extraction_paused("u", True)
    tool = MemoryTool(store)
    assert tool.remember_from_text("u", "我喜欢听粤剧") == []
    assert store.list("u") == []


def test_load_context_ignores_legacy_reminder_entries(tmp_path):
    store = MemoryStore(tmp_path)
    store.add("u", MemoryCategory.reminder_or_setting, "每天八点吃药")
    store.add("u", MemoryCategory.profile_preference, "喜欢粤剧")

    context = MemoryTool(store).load_context("u")

    assert [entry.content for entry in context] == ["喜欢粤剧"]
