"""Markdown-first memory store (issue #10).

Per user, under ``<memory_root>/users/{user_id}/``:
  - ``memory.md``    — human-readable source of truth (regenerated on change)
  - ``memories.json`` — structured index for reliable CRUD / queries

The markdown is the transparent artifact users and researchers read; the JSON
gives stable ids and fast lookups. (SQLite is the planned structured upgrade,
consistent with the profile/trace stores.)
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.memory import (
    MemoryCategory,
    MemoryEntry,
    MemorySettings,
)

_SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_CATEGORY_TITLES = {
    MemoryCategory.profile_preference: "偏好 (profile_preference)",
    MemoryCategory.event_memory: "事件 (event_memory)",
    MemoryCategory.reminder_or_setting: "提醒 / 设置 (reminder_or_setting)",
    MemoryCategory.boundary_preference: "边界偏好 (boundary_preference)",
}


class MemoryStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def _user_dir(self, user_id: str) -> Path:
        if not _SAFE_USER_ID.match(user_id):
            raise ValueError(f"invalid user_id: {user_id!r}")
        return self.base_dir / "users" / user_id

    def _json_path(self, user_id: str) -> Path:
        return self._user_dir(user_id) / "memories.json"

    def _load(self, user_id: str) -> dict:
        path = self._json_path(user_id)
        if not path.exists():
            return {"settings": {"extraction_paused": False}, "memories": []}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, user_id: str, data: dict) -> None:
        user_dir = self._user_dir(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        self._json_path(user_id).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self._render_markdown(user_id, data)

    # --- public API ---------------------------------------------------------

    def list(self, user_id: str) -> list[MemoryEntry]:
        data = self._load(user_id)
        return [MemoryEntry.model_validate(m) for m in data["memories"]]

    def get_settings(self, user_id: str) -> MemorySettings:
        return MemorySettings.model_validate(self._load(user_id)["settings"])

    def is_extraction_paused(self, user_id: str) -> bool:
        return self.get_settings(user_id).extraction_paused

    def add(
        self, user_id: str, category: MemoryCategory, content: str
    ) -> MemoryEntry:
        content = content.strip()
        data = self._load(user_id)
        entry = MemoryEntry(
            id=f"m_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            category=category,
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        data["memories"].append(entry.model_dump(mode="json"))
        self._save(user_id, data)
        return entry

    def add_if_absent(
        self, user_id: str, category: MemoryCategory, content: str
    ) -> MemoryEntry | None:
        """Add only if no entry with the same content exists. Returns the new
        entry, or None if it was a duplicate."""
        content = content.strip()
        existing = {m.content for m in self.list(user_id)}
        if content in existing:
            return None
        return self.add(user_id, category, content)

    def update_content(
        self, user_id: str, memory_id: str, content: str
    ) -> MemoryEntry | None:
        content = content.strip()
        data = self._load(user_id)
        for item in data["memories"]:
            if item["id"] != memory_id:
                continue
            item["content"] = content
            item["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save(user_id, data)
            return MemoryEntry.model_validate(item)
        return None

    def delete(self, user_id: str, memory_id: str) -> bool:
        data = self._load(user_id)
        before = len(data["memories"])
        data["memories"] = [m for m in data["memories"] if m["id"] != memory_id]
        if len(data["memories"]) == before:
            return False
        self._save(user_id, data)
        return True

    def set_extraction_paused(self, user_id: str, paused: bool) -> MemorySettings:
        data = self._load(user_id)
        data["settings"]["extraction_paused"] = paused
        self._save(user_id, data)
        return MemorySettings(extraction_paused=paused)

    # --- markdown rendering -------------------------------------------------

    def _render_markdown(self, user_id: str, data: dict) -> None:
        lines = [f"# {user_id} 的记忆", ""]
        paused = data["settings"].get("extraction_paused", False)
        lines.append(f"记忆提取：{'已暂停' if paused else '开启'}")
        lines.append("")
        for category in MemoryCategory:
            items = [m for m in data["memories"] if m["category"] == category.value]
            if not items:
                continue
            lines.append(f"## {_CATEGORY_TITLES[category]}")
            for m in items:
                lines.append(f"- {m['content']}")
            lines.append("")
        (self._user_dir(user_id) / "memory.md").write_text(
            "\n".join(lines).rstrip() + "\n", encoding="utf-8"
        )
