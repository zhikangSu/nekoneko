"""File-backed reminder store (issue #11).

One JSON file per user: ``<reminder_dir>/{user_id}.json`` holding a list of
reminders. Demo-scale; SQLite is the planned structured upgrade.
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.schemas.reminder import Recurrence, Reminder

_SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class ReminderStore:
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

    def list(self, user_id: str) -> list[Reminder]:
        return [Reminder.model_validate(r) for r in self._load(user_id)]

    def get(self, user_id: str, reminder_id: str) -> Optional[Reminder]:
        for r in self._load(user_id):
            if r["id"] == reminder_id:
                return Reminder.model_validate(r)
        return None

    def add(
        self,
        user_id: str,
        *,
        content: str,
        time: str,
        recurrence: Recurrence,
        date: Optional[str] = None,
    ) -> Reminder:
        items = self._load(user_id)
        reminder = Reminder(
            id=f"r_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            content=content.strip(),
            time=time,
            recurrence=recurrence,
            date=date,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        items.append(reminder.model_dump(mode="json"))
        self._save(user_id, items)
        return reminder

    def delete(self, user_id: str, reminder_id: str) -> bool:
        items = self._load(user_id)
        kept = [r for r in items if r["id"] != reminder_id]
        if len(kept) == len(items):
            return False
        self._save(user_id, kept)
        return True

    def confirm(self, user_id: str, reminder_id: str) -> Optional[Reminder]:
        items = self._load(user_id)
        updated: Optional[Reminder] = None
        for r in items:
            if r["id"] == reminder_id:
                r["last_confirmed_at"] = datetime.now(timezone.utc).isoformat()
                updated = Reminder.model_validate(r)
        if updated is not None:
            self._save(user_id, items)
        return updated
