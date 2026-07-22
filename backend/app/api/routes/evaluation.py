"""Evaluation export endpoints (issue #80)."""

from __future__ import annotations

import csv
import re
from datetime import datetime, timezone
from io import StringIO
from typing import Iterable

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.api.deps import get_trace_store
from app.schemas.evaluation import EvaluationExport
from app.schemas.trace import TraceSummary
from app.stores.trace_store import TraceStore

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


def _safe_filename_component(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "_", value)
    return cleaned or "export"


def _count_by(rows: Iterable[TraceSummary], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = getattr(row, field)
        key = value.value if hasattr(value, "value") else str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _build_export(user_id: str, rows: list[TraceSummary]) -> EvaluationExport:
    return EvaluationExport(
        user_id=user_id,
        exported_at=datetime.now(timezone.utc).isoformat(),
        trace_count=len(rows),
        route_counts=_count_by(rows, "route"),
        risk_counts=_count_by(rows, "risk_level"),
        safety_critic_turns=sum(1 for row in rows if row.safety_critic_used),
        retrieval_turns=sum(1 for row in rows if row.retrieval_used),
        rows=rows,
    )


@router.get("/export", response_model=EvaluationExport)
def export_evaluation_json(
    user_id: str = Query(default="demo_user", min_length=1, max_length=64),
    limit: int = Query(default=200, ge=1, le=1000),
    store: TraceStore = Depends(get_trace_store),
) -> EvaluationExport:
    rows = store.list(user_id=user_id, limit=limit)
    return _build_export(user_id, rows)


@router.get("/export.csv")
def export_evaluation_csv(
    user_id: str = Query(default="demo_user", min_length=1, max_length=64),
    limit: int = Query(default=200, ge=1, le=1000),
    store: TraceStore = Depends(get_trace_store),
) -> Response:
    export = _build_export(user_id, store.list(user_id=user_id, limit=limit))
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "turn_id",
            "created_at",
            "route",
            "risk_level",
            "safety_critic_used",
            "retrieval_used",
        ],
    )
    writer.writeheader()
    for row in export.rows:
        writer.writerow(
            {
                "turn_id": row.turn_id,
                "created_at": row.created_at,
                "route": row.route.value,
                "risk_level": row.risk_level.value,
                "safety_critic_used": row.safety_critic_used,
                "retrieval_used": row.retrieval_used,
            }
        )
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                "attachment; "
                f'filename="qaq-evaluation-{_safe_filename_component(user_id)}.csv"'
            )
        },
    )
