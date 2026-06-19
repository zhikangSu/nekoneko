"""File-backed UserProfile store (issue #21).

Persists one JSON file per user under a configurable directory. This is the
Slice-2 persistence; the structured SQLite store arrives with the memory slice
(#10). Kept behind this small interface so swapping the backend is local.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.schemas.profile import ProfileUpdate, UserProfile, normalize_name

# Restrict user_id to a safe, path-traversal-proof charset.
_SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

_NAME_FIELDS = {"companion_display_name", "user_display_name"}


class ProfileStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def _path(self, user_id: str) -> Path:
        if not _SAFE_USER_ID.match(user_id):
            raise ValueError(f"invalid user_id: {user_id!r}")
        return self.base_dir / f"{user_id}.json"

    def get(self, user_id: str) -> UserProfile:
        """Return the stored profile, or a fresh default (not persisted)."""
        path = self._path(user_id)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            data["user_id"] = user_id
            return UserProfile.model_validate(data)
        return UserProfile(user_id=user_id)

    def save(self, profile: UserProfile) -> UserProfile:
        path = self._path(profile.user_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(profile.model_dump(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return profile

    def update(self, user_id: str, update: ProfileUpdate) -> UserProfile:
        profile = self.get(user_id)
        changes = update.model_dump(exclude_unset=True)
        for field, value in changes.items():
            if field in _NAME_FIELDS:
                value = normalize_name(value)
            setattr(profile, field, value)
        return self.save(profile)
