"""Memory Center endpoints (issue #10, docs/05 §6.2).

    GET    /api/memory/{user_id}                 list + settings
    POST   /api/memory/{user_id}                 add a memory
    DELETE /api/memory/{user_id}/{memory_id}     delete a memory
    PATCH  /api/memory/{user_id}/settings        pause / resume extraction
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_memory_store
from app.schemas.memory import (
    MemoryCreate,
    MemoryEntry,
    MemorySettings,
    MemorySettingsUpdate,
    MemoryView,
)
from app.stores.memory_store import MemoryStore

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/{user_id}", response_model=MemoryView)
def get_memory(
    user_id: str,
    store: MemoryStore = Depends(get_memory_store),
) -> MemoryView:
    try:
        return MemoryView(
            user_id=user_id,
            settings=store.get_settings(user_id),
            memories=store.list(user_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{user_id}", response_model=MemoryEntry, status_code=201)
def add_memory(
    user_id: str,
    payload: MemoryCreate,
    store: MemoryStore = Depends(get_memory_store),
) -> MemoryEntry:
    try:
        return store.add(user_id, payload.category, payload.content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{user_id}/{memory_id}", status_code=204)
def delete_memory(
    user_id: str,
    memory_id: str,
    store: MemoryStore = Depends(get_memory_store),
) -> None:
    try:
        deleted = store.delete(user_id, memory_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="memory not found")


@router.patch("/{user_id}/settings", response_model=MemorySettings)
def update_settings(
    user_id: str,
    update: MemorySettingsUpdate,
    store: MemoryStore = Depends(get_memory_store),
) -> MemorySettings:
    try:
        if update.extraction_paused is None:
            return store.get_settings(user_id)
        return store.set_extraction_paused(user_id, update.extraction_paused)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
