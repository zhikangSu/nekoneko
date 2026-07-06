"""Authorized Memory Card endpoints (issue #54).

    POST /api/memory-cards/{user_id}/draft            propose a draft card
    GET  /api/memory-cards/{user_id}?status=pending   list a user's cards
    POST /api/memory-cards/{user_id}/{card_id}/action apply a user action

The companion drafts a candidate; nothing is written to long-term memory until
the user explicitly acts on the card. Sensitive content is only ever drafted
(``do_not_save_by_default``) and reaches memory solely on an explicit ``save``.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response

from app.api.deps import get_memory_card_store, get_memory_store
from app.schemas.memory_card import (
    CardStatus,
    MemoryCard,
    MemoryCardActionRequest,
    MemoryCardDraftRequest,
    MemoryCardList,
)
from app.stores.memory_card_store import MemoryCardStore
from app.stores.memory_store import MemoryStore
from app.tools.memory_card_tool import MemoryCardTool

router = APIRouter(prefix="/memory-cards", tags=["memory-cards"])


@router.post(
    "/{user_id}/draft",
    response_model=MemoryCard,
    responses={204: {"description": "No memory-card candidate found."}},
)
def draft_card(
    user_id: str,
    payload: MemoryCardDraftRequest,
    card_store: MemoryCardStore = Depends(get_memory_card_store),
    memory_store: MemoryStore = Depends(get_memory_store),
) -> Response:
    """Propose a draft card from an utterance. Returns 201 with the card, or
    204 (no body) when no candidate is found."""
    tool = MemoryCardTool(memory_store)
    try:
        card = tool.draft_from_text(user_id, payload.text, payload.source_turn_id)
        if card is None:
            return Response(status_code=204)
        saved = card_store.add(card)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return JSONResponse(status_code=201, content=saved.model_dump(mode="json"))


@router.get("/{user_id}", response_model=MemoryCardList)
def list_cards(
    user_id: str,
    status: Optional[CardStatus] = Query(default=None),
    card_store: MemoryCardStore = Depends(get_memory_card_store),
) -> MemoryCardList:
    try:
        return MemoryCardList(
            user_id=user_id, cards=card_store.list(user_id, status)
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{user_id}/{card_id}/action", response_model=MemoryCard)
def apply_card_action(
    user_id: str,
    card_id: str,
    payload: MemoryCardActionRequest,
    card_store: MemoryCardStore = Depends(get_memory_card_store),
    memory_store: MemoryStore = Depends(get_memory_store),
) -> MemoryCard:
    try:
        card = card_store.get(user_id, card_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if card is None:
        raise HTTPException(status_code=404, detail="memory card not found")
    # A card is single-use: only a pending card can be acted on, so a
    # double-click / retry can't write the same memory twice.
    if card.status != CardStatus.pending:
        raise HTTPException(
            status_code=409,
            detail=f"memory card already resolved (status={card.status.value})",
        )

    tool = MemoryCardTool(memory_store)
    try:
        updated = tool.apply_action(
            card, payload.action, payload.edited_summary, memory_store
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return card_store.update(updated)
