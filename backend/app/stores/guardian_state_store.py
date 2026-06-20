"""GuardianAgent welfare_state store (issue #12).

Cross-turn state per user: how many casual check-ins happened today, when each
event type was last surfaced (for cooldown), and which types the user refused
(paused). File-backed JSON; demo-scale.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

_SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class GuardianStateStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def _path(self, user_id: str) -> Path:
        if not _SAFE_USER_ID.match(user_id):
            raise ValueError(f"invalid user_id: {user_id!r}")
        return self.base_dir / f"{user_id}.json"

    def _load(self, user_id: str) -> dict:
        path = self._path(user_id)
        if not path.exists():
            return {"checkins": {"date": "", "count": 0}, "last_checkin_at": {}, "refused_until": {}}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save(self, user_id: str, data: dict) -> None:
        path = self._path(user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def checkins_today(self, user_id: str, now: datetime) -> int:
        data = self._load(user_id)
        if data["checkins"].get("date") == now.date().isoformat():
            return int(data["checkins"].get("count", 0))
        return 0

    def last_checkin_at(self, user_id: str, event_type: str) -> Optional[datetime]:
        value = self._load(user_id)["last_checkin_at"].get(event_type)
        return datetime.fromisoformat(value) if value else None

    def is_refused(self, user_id: str, event_type: str, now: datetime) -> bool:
        value = self._load(user_id)["refused_until"].get(event_type)
        return bool(value) and datetime.fromisoformat(value) > now

    def record_checkin(self, user_id: str, event_type: str, now: datetime) -> None:
        data = self._load(user_id)
        today = now.date().isoformat()
        if data["checkins"].get("date") != today:
            data["checkins"] = {"date": today, "count": 0}
        data["checkins"]["count"] = int(data["checkins"].get("count", 0)) + 1
        data["last_checkin_at"][event_type] = now.isoformat()
        self._save(user_id, data)

    def record_refusal(self, user_id: str, event_type: str, until: datetime) -> None:
        data = self._load(user_id)
        data["refused_until"][event_type] = until.isoformat()
        self._save(user_id, data)
