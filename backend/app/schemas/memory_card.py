"""Memory Card models (issue #54 — authorized Memory Card workflow).

A *Memory Card* is a draft candidate the companion proposes before anything is
written to long-term memory. Nothing is persisted to memory until the user
takes an explicit action (save / edit_then_save / reject / never_mention).

Classification is rule-based (no LLM). Sensitive content (老伴去世 / 生病 /
住院 / 家里矛盾 …) is NEVER auto-saved: its cards default to
``do_not_save_by_default`` and only reach memory on an explicit ``save``.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CandidateType(str, Enum):
    interest = "interest"
    fact = "fact"
    emotion = "emotion"
    sensitive = "sensitive"
    boundary_preference = "boundary_preference"
    role_preference = "role_preference"


class Sensitivity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class DefaultAction(str, Enum):
    suggest_save = "suggest_save"
    confirm_before_save = "confirm_before_save"
    do_not_save_by_default = "do_not_save_by_default"


class CardStatus(str, Enum):
    pending = "pending"
    saved = "saved"
    edited_saved = "edited_saved"
    rejected = "rejected"
    never_mention = "never_mention"


class CardAction(str, Enum):
    save = "save"
    edit_then_save = "edit_then_save"
    reject = "reject"
    never_mention = "never_mention"


class MemoryCard(BaseModel):
    card_id: str
    user_id: str
    candidate_type: CandidateType
    summary: str
    why_save: str
    sensitivity: Sensitivity
    default_action: DefaultAction
    source_turn_id: Optional[str] = None
    status: CardStatus = CardStatus.pending
    created_at: str


class MemoryCardDraftRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    source_turn_id: Optional[str] = None


class MemoryCardActionRequest(BaseModel):
    action: CardAction
    edited_summary: Optional[str] = Field(default=None, max_length=500)


class MemoryCardList(BaseModel):
    """GET /api/memory-cards/{user_id} response."""

    user_id: str
    cards: list[MemoryCard]
