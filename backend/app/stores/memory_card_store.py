"""File-backed Memory Card store (issue #54).

One JSON file per user: ``<cards_dir>/{user_id}.json`` holding the list of the
user's Memory Cards (drafts + resolved). Demo-scale; mirrors the style of
``ReminderStore`` (one JSON list per user). Cards live in a ``cards`` dir
beside the memory store's root.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from app.schemas.memory_card import CardStatus, MemoryCard

_SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class MemoryCardStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def _path(self, user_id: str) -> Path:
        if not _SAFE_USER_ID.match(user_id):
            raise ValueError(f"invalid user_id: {user_id!r}")
        return self.base_dir / f"{user_id}.json"

    def _load(self, user_id: str) -> list[dict]:
        path = self._path(user_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, user_id: str, items: list[dict]) -> None:
        path = self._path(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # --- public API ---------------------------------------------------------

    def add(self, card: MemoryCard) -> MemoryCard:
        items = self._load(card.user_id)
        items.append(card.model_dump(mode="json"))
        self._save(card.user_id, items)
        return card

    def list(
        self, user_id: str, status: Optional[CardStatus] = None
    ) -> list[MemoryCard]:
        cards = [MemoryCard.model_validate(c) for c in self._load(user_id)]
        if status is not None:
            cards = [c for c in cards if c.status == status]
        return cards

    def get(self, user_id: str, card_id: str) -> Optional[MemoryCard]:
        for c in self._load(user_id):
            if c["card_id"] == card_id:
                return MemoryCard.model_validate(c)
        return None

    def update(self, card: MemoryCard) -> MemoryCard:
        items = self._load(card.user_id)
        found = False
        for i, c in enumerate(items):
            if c["card_id"] == card.card_id:
                items[i] = card.model_dump(mode="json")
                found = True
                break
        if not found:
            raise ValueError(f"card not found: {card.card_id!r}")
        self._save(card.user_id, items)
        return card
