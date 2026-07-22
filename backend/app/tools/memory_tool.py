"""MemoryTool — read/write/extract long-term memory (issue #10/#81).

Wraps ``MemoryStore``. Stage 1 memory triage (#81) moved candidate extraction
into ``MemoryCandidateExtractor`` so chat writes can pass through a single
policy layer instead of silently bypassing authorized Memory Cards.
"""

from __future__ import annotations

from app.schemas.memory_candidate import MemoryCandidate
from app.schemas.memory import MemoryCategory, MemoryEntry
from app.schemas.memory_card import CandidateType
from app.stores.memory_store import MemoryStore
from app.tools.memory_candidate_extractor import MemoryCandidateExtractor


class MemoryTool:
    name = "MemoryTool"

    def __init__(self, store: MemoryStore):
        self._store = store
        self._extractor = MemoryCandidateExtractor()

    def load_context(self, user_id: str) -> list[MemoryEntry]:
        # Keep legacy reminder/setting entries readable through the memory API,
        # but do not feed operational reminders into companion context. New
        # reminders belong exclusively to ReminderStore.
        return [
            entry
            for entry in self._store.list(user_id)
            if entry.category != MemoryCategory.reminder_or_setting
        ]

    def is_extraction_paused(self, user_id: str) -> bool:
        return self._store.is_extraction_paused(user_id)

    def extract_preferences(self, text: str) -> list[str]:
        return self._extractor.extract_preferences(text)

    def save_candidate(
        self, user_id: str, candidate: MemoryCandidate
    ) -> MemoryEntry | None:
        if candidate.candidate_type == CandidateType.interest:
            category = MemoryCategory.profile_preference
        elif candidate.candidate_type == CandidateType.boundary_preference:
            category = MemoryCategory.boundary_preference
        else:
            category = MemoryCategory.event_memory
        return self._store.add_if_absent(user_id, category, candidate.summary)

    def update_candidate(
        self, user_id: str, memory_id: str, candidate: MemoryCandidate
    ) -> MemoryEntry | None:
        existing = next(
            (m for m in self._store.list(user_id) if m.id == memory_id), None
        )
        if existing is None:
            return None
        content = (
            candidate.summary
            if len(candidate.summary) > len(existing.content)
            else existing.content
        )
        return self._store.update_content(user_id, memory_id, content)

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
