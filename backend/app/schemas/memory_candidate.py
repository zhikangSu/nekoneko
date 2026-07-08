"""Memory candidate and triage models for the Stage 1 memory policy (#81).

Candidates are extracted from a single user turn, then routed by
MemoryTriagePolicy. The policy decides whether to auto-save, draft a Memory
Card, or ignore the candidate; extraction itself never writes long-term memory.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.memory_card import CandidateType, Sensitivity


class MemoryTriageAction(str, Enum):
    auto_save = "auto_save"
    create_card = "create_card"
    ignore = "ignore"
    create_boundary_card = "create_boundary_card"
    update_existing = "update_existing"


class MemoryCandidate(BaseModel):
    candidate_type: CandidateType
    summary: str = Field(min_length=1, max_length=500)
    evidence_text: str = Field(min_length=1, max_length=1000)
    sensitivity: Sensitivity
    confidence: float = Field(ge=0.0, le=1.0)
    source_turn_id: Optional[str] = None
    recommended_action: MemoryTriageAction


class MemoryTriageDecision(BaseModel):
    action: MemoryTriageAction
    reason: str
    ask_now: bool = False
    cooldown_applied: bool = False
