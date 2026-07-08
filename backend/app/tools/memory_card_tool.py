"""MemoryCardTool — rule-based Memory Card drafting + authorized apply (issue #54).

Turns a single user utterance into a *draft* Memory Card (or nothing) using a
deterministic, rule-based classifier (NO LLM). The card is only ever persisted
to long-term memory when the user takes an explicit action.

Classifier priority (first match wins):

    1. boundary_preference   — 「我不想再聊X」「别再提X」…  (protective)
    2. sensitive             — 老伴去世 / 生病 / 住院 / 家里矛盾 …
    3. role_preference       — 「我更喜欢同龄人陪我聊」…
    4. fact                  — 「我年轻时做过X」「我是X」…
    5. emotion               — an experience tied to an emotion word
    6. interest              — 「我喜欢X」「我爱X」

So 「我不想再聊老伴去世的事」→ boundary_preference (not sensitive), because
the user is drawing a boundary, and that boundary must be honoured.

Safety: sensitive cards default to ``do_not_save_by_default`` and are NEVER
auto-saved — they only reach memory on an explicit ``save`` action. No
medical-diagnosis memory is ever produced; 故人 content is never used to
impersonate the deceased — it is stored (if the user saves it) as a plain
event memory only.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.schemas.memory import MemoryCategory
from app.schemas.memory_candidate import MemoryCandidate
from app.schemas.memory_card import (
    CandidateType,
    CardAction,
    CardStatus,
    DefaultAction,
    MemoryCard,
)
from app.stores.memory_store import MemoryStore
from app.tools.memory_candidate_extractor import MemoryCandidateExtractor


class MemoryCardTool:
    name = "MemoryCardTool"

    def __init__(self, store: MemoryStore):
        self._store = store
        self._extractor = MemoryCandidateExtractor()

    # --- classification -----------------------------------------------------

    def classify(self, text: str) -> dict | None:
        """Rule-based classification. Returns a dict with candidate_type,
        summary, why_save, sensitivity, default_action — or ``None`` when no
        candidate is found. Priority: boundary → sensitive → role preference →
        fact → emotion → interest."""
        candidate = self._extractor.extract_one(text)
        if candidate is None:
            return None
        return {
            "candidate_type": candidate.candidate_type,
            "summary": candidate.summary,
            "why_save": self._why_save(candidate),
            "sensitivity": candidate.sensitivity,
            "default_action": self._default_action(candidate),
        }

    @staticmethod
    def _why_save(candidate: MemoryCandidate) -> str:
        if candidate.candidate_type == CandidateType.boundary_preference:
            return "记录一条边界偏好，以后避免主动提起这个话题。"
        if candidate.candidate_type == CandidateType.sensitive:
            return "这是敏感话题，只有您明确同意才会保存，默认不保存。"
        if candidate.candidate_type == CandidateType.fact:
            return "这是关于您的一段经历/事实，保存后我可以更了解您。"
        if candidate.candidate_type == CandidateType.emotion:
            return "这段经历带着情感，保存后我可以在合适时候陪您回忆。"
        if candidate.candidate_type == CandidateType.role_preference:
            return "这是您对互动方式的偏好，保存前需要您确认。"
        return "记录一个您的兴趣，方便以后一起聊。"

    @staticmethod
    def _default_action(candidate: MemoryCandidate) -> DefaultAction:
        if candidate.candidate_type == CandidateType.sensitive:
            return DefaultAction.do_not_save_by_default
        if candidate.candidate_type == CandidateType.interest:
            return DefaultAction.suggest_save
        return DefaultAction.confirm_before_save

    # --- drafting -----------------------------------------------------------

    def draft_from_text(
        self, user_id: str, text: str, source_turn_id: str | None = None
    ) -> MemoryCard | None:
        """Build a pending draft card from an utterance, or ``None`` if no
        candidate is found. Does NOT persist anything to long-term memory."""
        candidate = self._extractor.extract_one(text, source_turn_id)
        if candidate is None:
            return None
        return self.draft_from_candidate(user_id, candidate)

    def draft_from_candidate(
        self, user_id: str, candidate: MemoryCandidate
    ) -> MemoryCard:
        """Build a pending draft card from an already-triaged candidate."""
        return MemoryCard(
            card_id=f"mc_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            candidate_type=candidate.candidate_type,
            summary=candidate.summary,
            why_save=self._why_save(candidate),
            sensitivity=candidate.sensitivity,
            default_action=self._default_action(candidate),
            source_turn_id=candidate.source_turn_id,
            status=CardStatus.pending,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    # --- authorized apply ---------------------------------------------------

    @staticmethod
    def _save_category(candidate_type: CandidateType) -> MemoryCategory:
        """Long-term memory category for a save / edit_then_save action."""
        if candidate_type in {CandidateType.interest, CandidateType.role_preference}:
            return MemoryCategory.profile_preference
        if candidate_type == CandidateType.boundary_preference:
            return MemoryCategory.boundary_preference
        # fact / emotion / sensitive → event memory
        return MemoryCategory.event_memory

    def apply_action(
        self,
        card: MemoryCard,
        action: CardAction,
        edited_summary: str | None,
        memory_store: MemoryStore,
    ) -> MemoryCard:
        """Apply an authorized user action, mutating and returning the card.

        - save            → write ``summary`` into long-term memory; status=saved.
        - edit_then_save  → write ``edited_summary``; status=edited_saved.
        - reject          → write nothing; status=rejected.
        - never_mention   → write an avoid-rule into ``boundary_preference``
                            memory; status=never_mention.
        """
        if action == CardAction.reject:
            card.status = CardStatus.rejected
            return card

        if action == CardAction.never_mention:
            memory_store.add(
                card.user_id,
                MemoryCategory.boundary_preference,
                f"以后不要再提：{card.summary}",
            )
            card.status = CardStatus.never_mention
            return card

        if action == CardAction.save:
            memory_store.add(
                card.user_id,
                self._save_category(card.candidate_type),
                card.summary,
            )
            card.status = CardStatus.saved
            return card

        if action == CardAction.edit_then_save:
            new_summary = (edited_summary or "").strip()
            if not new_summary:
                raise ValueError("edited_summary is required for edit_then_save")
            card.summary = new_summary
            memory_store.add(
                card.user_id,
                self._save_category(card.candidate_type),
                new_summary,
            )
            card.status = CardStatus.edited_saved
            return card

        raise ValueError(f"unsupported action: {action!r}")
