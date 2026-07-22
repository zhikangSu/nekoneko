"""File-backed trace store (issue #9).

Persists one JSON file per turn under a configurable directory so the Trace
Panel can show history by ``turn_id`` and a recent list per user. Demo-scale;
no DB. Mirrors the docs/05 §7.3 ``data/traces/{turn_id}.json`` recommendation.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from app.schemas.trace import TraceRecord, TraceSummary

_SAFE_TURN_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class TraceStore:
    def __init__(self, base_dir: str | Path):
        self.base_dir = Path(base_dir)

    def _path(self, turn_id: str) -> Path:
        if not _SAFE_TURN_ID.match(turn_id):
            raise ValueError(f"invalid turn_id: {turn_id!r}")
        return self.base_dir / f"{turn_id}.json"

    def save(self, record: TraceRecord) -> TraceRecord:
        path = self._path(record.turn_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return record

    def get(self, turn_id: str) -> Optional[TraceRecord]:
        path = self._path(turn_id)
        if not path.exists():
            return None
        return TraceRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def list(
        self, user_id: Optional[str] = None, limit: Optional[int] = 20
    ) -> list[TraceSummary]:
        if not self.base_dir.exists():
            return []
        records: list[TraceRecord] = []
        for path in self.base_dir.glob("*.json"):
            try:
                records.append(
                    TraceRecord.model_validate_json(path.read_text(encoding="utf-8"))
                )
            except (ValueError, OSError):
                continue  # skip malformed files
        if user_id is not None:
            records = [r for r in records if r.user_id == user_id]
        records.sort(key=lambda r: r.created_at, reverse=True)
        if limit is not None:
            records = records[: max(0, limit)]
        return [
            TraceSummary(
                turn_id=r.turn_id,
                user_id=r.user_id,
                created_at=r.created_at,
                route=r.trace.route,
                risk_level=r.trace.risk_level,
                safety_critic_used=r.trace.safety_critic_used,
                retrieval_used=r.trace.retrieval_used,
            )
            for r in records
        ]
