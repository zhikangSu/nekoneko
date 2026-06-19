"""MemoryTool — read/write/extract long-term memory (issue #10).

Wraps ``MemoryStore`` and adds a deterministic preference extractor for demo
mode (no LLM): clear statements like 「我喜欢听粤剧」become a
``profile_preference`` memory. Extraction is skipped while the user has paused
memory. Onboarding / companion_display_name are NOT handled here (that's #21).
"""

from __future__ import annotations

import re

from app.schemas.memory import MemoryCategory, MemoryEntry
from app.stores.memory_store import MemoryStore

# Capture the object of a clear like/love statement, stopping at punctuation.
_PREFERENCE_PATTERNS = (
    re.compile(r"我(?:很|最|平时|特别|真的)?喜欢([^，。、!！?？\s]{1,20})"),
    re.compile(r"我(?:很|最)?爱([^，。、!！?？\s]{1,20})"),
)


class MemoryTool:
    name = "MemoryTool"

    def __init__(self, store: MemoryStore):
        self._store = store

    def load_context(self, user_id: str) -> list[MemoryEntry]:
        return self._store.list(user_id)

    def extract_preferences(self, text: str) -> list[str]:
        found: list[str] = []
        for pattern in _PREFERENCE_PATTERNS:
            for match in pattern.finditer(text or ""):
                obj = match.group(1).strip()
                content = f"喜欢{obj}"
                if obj and content not in found:
                    found.append(content)
        return found

    def remember_from_text(self, user_id: str, text: str) -> list[MemoryEntry]:
        """Extract and persist new preferences, unless extraction is paused."""
        if self._store.is_extraction_paused(user_id):
            return []
        saved: list[MemoryEntry] = []
        for content in self.extract_preferences(text):
            entry = self._store.add_if_absent(
                user_id, MemoryCategory.profile_preference, content
            )
            if entry is not None:
                saved.append(entry)
        return saved
