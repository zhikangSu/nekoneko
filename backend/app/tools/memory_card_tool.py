"""MemoryCardTool — rule-based Memory Card drafting + authorized apply (issue #54).

Turns a single user utterance into a *draft* Memory Card (or nothing) using a
deterministic, rule-based classifier (NO LLM). The card is only ever persisted
to long-term memory when the user takes an explicit action.

Classifier priority (first match wins):

    1. boundary_preference   — 「我不想再聊X」「别再提X」…  (protective)
    2. sensitive             — 老伴去世 / 生病 / 住院 / 家里矛盾 …
    3. fact                  — 「我年轻时做过X」「我是X」…
    4. emotion               — an experience tied to an emotion word
    5. interest              — 「我喜欢X」「我爱X」

So 「我不想再聊老伴去世的事」→ boundary_preference (not sensitive), because
the user is drawing a boundary, and that boundary must be honoured.

Safety: sensitive cards default to ``do_not_save_by_default`` and are NEVER
auto-saved — they only reach memory on an explicit ``save`` action. No
medical-diagnosis memory is ever produced; 故人 content is never used to
impersonate the deceased — it is stored (if the user saves it) as a plain
event memory only.
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from app.schemas.memory import MemoryCategory
from app.schemas.memory_card import (
    CandidateType,
    CardAction,
    CardStatus,
    DefaultAction,
    MemoryCard,
    Sensitivity,
)
from app.stores.memory_store import MemoryStore

# --- rule vocabularies -------------------------------------------------------

# Boundary preference: the user asks to stop / avoid a topic. Highest priority
# so a boundary about a sensitive topic is treated as a boundary, not re-surfaced.
_BOUNDARY_PATTERNS = (
    re.compile(r"我不想(?:再)?聊([^，。、!！?？\s]{1,20})"),
    re.compile(r"不想聊([^，。、!！?？\s]{1,20})"),
    re.compile(r"(?:以后)?别(?:再)?提([^，。、!！?？\s]{1,20})"),
    re.compile(r"不(?:喜欢|想)聊([^，。、!！?？\s]{1,20})"),
)
# Softer boundary phrasing that names no clean object (e.g. 不喜欢某个角色).
_BOUNDARY_KEYWORDS = ("不想再聊", "不想聊", "别再提", "别提", "以后别提", "不喜欢聊", "不喜欢某")

# Sensitive: bereavement, illness, hospitalization, family conflict, privacy.
_SENSITIVE_KEYWORDS = (
    "老伴去世",
    "老伴走了",
    "去世",
    "过世",
    "走了",
    "生病",
    "住院",
    "家里矛盾",
    "吵架",
    "隐私",
)

# Emotion words: an experience tied to one of these is an ``emotion`` card.
_EMOTION_KEYWORDS = ("骄傲", "自豪", "难过", "开心", "遗憾", "后悔", "想念")

# Fact: life-history statements. Capture the object after the trigger phrase.
_FACT_PATTERNS = (
    re.compile(r"我年轻时(?:做过|当过|是)([^，。、!！?？\s]{1,30})"),
    re.compile(r"我以前(?:做过|当过|是|住过)([^，。、!！?？\s]{1,30})"),
    re.compile(r"我做过([^，。、!！?？\s]{1,30})"),
    re.compile(r"我当过([^，。、!！?？\s]{1,30})"),
    re.compile(r"我住过([^，。、!！?？\s]{1,30})"),
    re.compile(r"我是([^，。、!！?？\s]{1,30})"),
)

# Interest: clear like/love statements.
_INTEREST_PATTERNS = (
    re.compile(r"我(?:很|最|平时|特别|真的)?喜欢([^，。、!！?？\s]{1,20})"),
    re.compile(r"我(?:很|最)?爱([^，。、!！?？\s]{1,20})"),
)


def _first_group(patterns, text: str) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            obj = match.group(1).strip()
            if obj:
                return obj
    return None


class MemoryCardTool:
    name = "MemoryCardTool"

    def __init__(self, store: MemoryStore):
        self._store = store

    # --- classification -----------------------------------------------------

    def classify(self, text: str) -> dict | None:
        """Rule-based classification. Returns a dict with candidate_type,
        summary, why_save, sensitivity, default_action — or ``None`` when no
        candidate is found. Priority: boundary → sensitive → fact → emotion →
        interest."""
        text = (text or "").strip()
        if not text:
            return None

        # 1) boundary_preference (highest priority — honour the user's boundary)
        boundary_obj = _first_group(_BOUNDARY_PATTERNS, text)
        if boundary_obj is not None:
            summary = f"不想再聊{boundary_obj}"
            is_boundary = True
        elif any(k in text for k in _BOUNDARY_KEYWORDS):
            # A boundary phrase matched but named no clean object; keep the
            # user's own wording verbatim instead of double-prefixing it.
            summary = text
            is_boundary = True
        else:
            is_boundary = False
        if is_boundary:
            return {
                "candidate_type": CandidateType.boundary_preference,
                "summary": summary,
                "why_save": "记录一条边界偏好，以后避免主动提起这个话题。",
                "sensitivity": Sensitivity.medium,
                # Treat a boundary as a protective suggestion the user can confirm.
                "default_action": DefaultAction.confirm_before_save,
            }

        # 2) sensitive (never auto-saved)
        sensitive_hit = next((k for k in _SENSITIVE_KEYWORDS if k in text), None)
        if sensitive_hit is not None:
            return {
                "candidate_type": CandidateType.sensitive,
                "summary": text,
                "why_save": "这是敏感话题，只有您明确同意才会保存，默认不保存。",
                "sensitivity": Sensitivity.high,
                "default_action": DefaultAction.do_not_save_by_default,
            }

        # 3) fact
        fact_obj = _first_group(_FACT_PATTERNS, text)
        if fact_obj is not None:
            return {
                "candidate_type": CandidateType.fact,
                "summary": text,
                "why_save": "这是关于您的一段经历/事实，保存后我可以更了解您。",
                "sensitivity": Sensitivity.low,
                "default_action": DefaultAction.confirm_before_save,
            }

        # 4) emotion (an experience tied to an emotion word)
        emotion_hit = next((k for k in _EMOTION_KEYWORDS if k in text), None)
        if emotion_hit is not None:
            return {
                "candidate_type": CandidateType.emotion,
                "summary": text,
                "why_save": "这段经历带着情感，保存后我可以在合适时候陪您回忆。",
                "sensitivity": Sensitivity.medium,
                "default_action": DefaultAction.confirm_before_save,
            }

        # 5) interest
        interest_obj = _first_group(_INTEREST_PATTERNS, text)
        if interest_obj is not None:
            return {
                "candidate_type": CandidateType.interest,
                "summary": f"喜欢{interest_obj}",
                "why_save": "记录一个您的兴趣，方便以后一起聊。",
                "sensitivity": Sensitivity.low,
                "default_action": DefaultAction.suggest_save,
            }

        return None

    # --- drafting -----------------------------------------------------------

    def draft_from_text(
        self, user_id: str, text: str, source_turn_id: str | None = None
    ) -> MemoryCard | None:
        """Build a pending draft card from an utterance, or ``None`` if no
        candidate is found. Does NOT persist anything to long-term memory."""
        result = self.classify(text)
        if result is None:
            return None
        return MemoryCard(
            card_id=f"mc_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            candidate_type=result["candidate_type"],
            summary=result["summary"],
            why_save=result["why_save"],
            sensitivity=result["sensitivity"],
            default_action=result["default_action"],
            source_turn_id=source_turn_id,
            status=CardStatus.pending,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    # --- authorized apply ---------------------------------------------------

    @staticmethod
    def _save_category(candidate_type: CandidateType) -> MemoryCategory:
        """Long-term memory category for a save / edit_then_save action."""
        if candidate_type == CandidateType.interest:
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
