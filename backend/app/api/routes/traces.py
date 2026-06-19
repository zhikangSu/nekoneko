"""Agent trace history endpoints (issue #9).

    GET /api/traces/{turn_id}          one persisted trace
    GET /api/traces?user_id=&limit=    recent traces (compact summaries)
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_trace_store
from app.schemas.trace import TraceRecord, TraceSummary
from app.stores.trace_store import TraceStore

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/{turn_id}", response_model=TraceRecord)
def get_trace(
    turn_id: str,
    store: TraceStore = Depends(get_trace_store),
) -> TraceRecord:
    try:
        record = store.get(turn_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if record is None:
        raise HTTPException(status_code=404, detail="trace not found")
    return record


@router.get("", response_model=list[TraceSummary])
def list_traces(
    user_id: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=200),
    store: TraceStore = Depends(get_trace_store),
) -> list[TraceSummary]:
    return store.list(user_id=user_id, limit=limit)
