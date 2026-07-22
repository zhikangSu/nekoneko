"""MemoryTriagePolicy for authorized, low-noise memory handling (#81)."""

from __future__ import annotations

from app.schemas.memory import MemoryEntry
from app.schemas.memory_candidate import (
    MemoryCandidate,
    MemoryTriageAction,
    MemoryTriageDecision,
)
from app.schemas.memory_card import CandidateType, CardStatus, MemoryCard
from app.services.memory_similarity import MemorySimilarityService


class MemoryTriagePolicy:
    name = "MemoryTriagePolicy"

    def __init__(self, similarity: MemorySimilarityService | None = None):
        self._similarity = similarity or MemorySimilarityService()

    def decide(
        self,
        candidate: MemoryCandidate,
        *,
        existing_memories: list[MemoryEntry],
        existing_cards: list[MemoryCard] | None = None,
    ) -> MemoryTriageDecision:
        matched = self._find_similar_memory(candidate, existing_memories)
        if matched is not None:
            if self._similarity.is_duplicate(candidate.summary, matched.content):
                return MemoryTriageDecision(
                    action=MemoryTriageAction.ignore,
                    reason="重复内容：相同长期记忆已存在，不重复保存。",
                    ask_now=False,
                    cooldown_applied=True,
                    target_memory_id=matched.id,
                )
            return MemoryTriageDecision(
                action=MemoryTriageAction.update_existing,
                reason="相似长期记忆已存在，更新原有记忆而非重复保存。",
                ask_now=False,
                cooldown_applied=True,
                target_memory_id=matched.id,
            )

        if self._has_similar_card(candidate, existing_cards or []):
            return MemoryTriageDecision(
                action=MemoryTriageAction.ignore,
                reason="重复内容：相似 Memory Card 已存在，避免重复打扰。",
                ask_now=False,
                cooldown_applied=True,
            )

        if candidate.candidate_type == CandidateType.interest:
            return MemoryTriageDecision(
                action=MemoryTriageAction.auto_save,
                reason="低敏明确兴趣偏好，静默保存到 Memory Center，可随时删除。",
                ask_now=False,
            )

        if candidate.candidate_type == CandidateType.boundary_preference:
            return MemoryTriageDecision(
                action=MemoryTriageAction.create_boundary_card,
                reason="这是互动边界偏好，会影响后续主动提起的话题，需用户确认。",
                ask_now=True,
            )

        if candidate.candidate_type == CandidateType.sensitive:
            return MemoryTriageDecision(
                action=MemoryTriageAction.ignore,
                reason="敏感内容默认不保存，也不主动询问，除非用户明确要求。",
                ask_now=False,
            )

        if candidate.candidate_type == CandidateType.emotion:
            return MemoryTriageDecision(
                action=MemoryTriageAction.create_card,
                reason="情感经历可作为候选卡片延后确认，避免打断当前陪伴。",
                ask_now=False,
            )

        if candidate.candidate_type in {
            CandidateType.fact,
            CandidateType.role_preference,
        }:
            return MemoryTriageDecision(
                action=MemoryTriageAction.create_card,
                reason="这类长期事实或互动偏好需要用户授权后保存。",
                ask_now=True,
            )

        return MemoryTriageDecision(
            action=MemoryTriageAction.ignore,
            reason="未达到长期记忆保存阈值。",
            ask_now=False,
        )

    def _find_similar_memory(
        self, candidate: MemoryCandidate, existing: list[MemoryEntry]
    ) -> MemoryEntry | None:
        for item in existing:
            if self._similarity.is_similar(candidate.summary, item.content):
                return item
        return None

    def _has_similar_card(
        self, candidate: MemoryCandidate, existing: list[MemoryCard]
    ) -> bool:
        return any(
            card.status == CardStatus.pending
            and card.candidate_type == candidate.candidate_type
            and self._similarity.is_similar(candidate.summary, card.summary)
            for card in existing
        )
