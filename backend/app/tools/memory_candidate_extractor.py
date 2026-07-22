"""Rule-based memory candidate extraction for Stage 1 (#81).

The extractor is shared by MemoryTool, MemoryCardTool, and the graph memory
write node so there is one deterministic source of candidate logic. It extracts
at most one candidate per turn in priority order to keep the demo low-noise.
"""

from __future__ import annotations

import re

from app.schemas.memory_candidate import MemoryCandidate, MemoryTriageAction
from app.schemas.memory_card import CandidateType, Sensitivity

# Boundary preference: the user asks to stop / avoid a topic. Highest priority
# so a boundary about a sensitive topic is treated as a boundary, not re-surfaced.
_BOUNDARY_PATTERNS = (
    re.compile(r"我不想(?:再)?聊([^，。、!！?？\s]{1,30})"),
    re.compile(r"不想聊([^，。、!！?？\s]{1,30})"),
    re.compile(r"(?:以后)?别(?:再)?提([^，。、!！?？\s]{1,30})"),
    re.compile(r"不要(?:再)?问(?:我)?([^，。、!！?？\s]{1,30})"),
    re.compile(r"不(?:喜欢|想)聊([^，。、!！?？\s]{1,30})"),
)
_BOUNDARY_KEYWORDS = (
    "不想再聊",
    "不想聊",
    "别再提",
    "别提",
    "以后别提",
    "不要再问",
    "不喜欢聊",
    "不喜欢连续追问",
)

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

_ROLE_PREFERENCE_PATTERNS = (
    re.compile(r"我(?:更|比较)?喜欢([^，。、!！?？\s]{1,20})(?:陪我聊|跟我聊|陪我说|来问)"),
    re.compile(r"我(?:更|比较)?想让([^，。、!！?？\s]{1,20})(?:陪我聊|跟我聊|陪我说)"),
    re.compile(r"我(?:更|比较)?喜欢([^，。、!！?？\s]{1,20})的(?:说话|聊天)方式"),
    re.compile(r"别像([^，。、!！?？\s]{1,20})那样(?:一直)?问"),
)

_FACT_PATTERNS = (
    re.compile(r"我年轻时(?:做过|当过|是)([^，。、!！?？\s]{1,30})"),
    re.compile(r"我以前(?:做过|当过|是|住过)([^，。、!！?？\s]{1,30})"),
    re.compile(r"我做过([^，。、!！?？\s]{1,30})"),
    re.compile(r"我当过([^，。、!！?？\s]{1,30})"),
    re.compile(r"我住过([^，。、!！?？\s]{1,30})"),
    re.compile(r"我是([^，。、!！?？\s]{1,30})"),
)

_EMOTION_KEYWORDS = ("骄傲", "自豪", "难过", "开心", "遗憾", "后悔", "想念")

_INTEREST_PATTERNS = (
    re.compile(r"我(?:很|最|平时|特别|真的)?喜欢([^，。、!！?？\s]{1,20})"),
    re.compile(r"我(?:很|最)?爱([^，。、!！?？\s]{1,20})"),
)

_TEMPORARY_EMOTION_MARKERS = (
    "今天有点烦",
    "今天很烦",
    "现在有点烦",
    "今天心情不好",
    "现在心情不好",
)

# Interrogative / uncertainty markers: questions like “我是不是老糊涂了” must not
# be stored as facts or preferences.
_QUESTION_MARKERS = (
    "是不是",
    "吗",
    "呢",
    "怎么",
    "为什么",
    "什么",
    "能不能",
    "好不好",
    "有没有",
    "是否",
)


def _is_question(text: str) -> bool:
    if "？" in text or "?" in text:
        return True
    return any(marker in text for marker in _QUESTION_MARKERS)


def _first_group(patterns, text: str) -> str | None:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            obj = match.group(1).strip()
            if obj:
                return obj
    return None


class MemoryCandidateExtractor:
    name = "MemoryCandidateExtractor"

    def extract_one(
        self, text: str, source_turn_id: str | None = None
    ) -> MemoryCandidate | None:
        text = (text or "").strip()
        if not text:
            return None

        boundary_obj = _first_group(_BOUNDARY_PATTERNS, text)
        if boundary_obj is not None:
            summary = f"不想再聊{boundary_obj}"
            return MemoryCandidate(
                candidate_type=CandidateType.boundary_preference,
                summary=summary,
                evidence_text=text,
                sensitivity=Sensitivity.medium,
                confidence=0.92,
                source_turn_id=source_turn_id,
                recommended_action=MemoryTriageAction.create_boundary_card,
            )
        if any(k in text for k in _BOUNDARY_KEYWORDS):
            return MemoryCandidate(
                candidate_type=CandidateType.boundary_preference,
                summary=text,
                evidence_text=text,
                sensitivity=Sensitivity.medium,
                confidence=0.82,
                source_turn_id=source_turn_id,
                recommended_action=MemoryTriageAction.create_boundary_card,
            )

        sensitive_hit = next((k for k in _SENSITIVE_KEYWORDS if k in text), None)
        if sensitive_hit is not None:
            return MemoryCandidate(
                candidate_type=CandidateType.sensitive,
                summary=text,
                evidence_text=text,
                sensitivity=Sensitivity.high,
                confidence=0.86,
                source_turn_id=source_turn_id,
                recommended_action=MemoryTriageAction.ignore,
            )

        if _is_question(text):
            return None

        role_obj = _first_group(_ROLE_PREFERENCE_PATTERNS, text)
        if role_obj is not None:
            if "别像" in text:
                summary = f"不喜欢像{role_obj}那样一直问"
            else:
                summary = f"偏好{role_obj}陪聊"
            return MemoryCandidate(
                candidate_type=CandidateType.role_preference,
                summary=summary,
                evidence_text=text,
                sensitivity=Sensitivity.medium,
                confidence=0.78,
                source_turn_id=source_turn_id,
                recommended_action=MemoryTriageAction.create_card,
            )

        fact_obj = _first_group(_FACT_PATTERNS, text)
        if fact_obj is not None:
            return MemoryCandidate(
                candidate_type=CandidateType.fact,
                summary=text,
                evidence_text=text,
                sensitivity=Sensitivity.low,
                confidence=0.8,
                source_turn_id=source_turn_id,
                recommended_action=MemoryTriageAction.create_card,
            )

        if not any(marker in text for marker in _TEMPORARY_EMOTION_MARKERS):
            emotion_hit = next((k for k in _EMOTION_KEYWORDS if k in text), None)
            if emotion_hit is not None:
                return MemoryCandidate(
                    candidate_type=CandidateType.emotion,
                    summary=text,
                    evidence_text=text,
                    sensitivity=Sensitivity.medium,
                    confidence=0.68,
                    source_turn_id=source_turn_id,
                    recommended_action=MemoryTriageAction.create_card,
                )

        interest_obj = _first_group(_INTEREST_PATTERNS, text)
        if interest_obj is not None:
            return MemoryCandidate(
                candidate_type=CandidateType.interest,
                summary=f"喜欢{interest_obj}",
                evidence_text=text,
                sensitivity=Sensitivity.low,
                confidence=0.9,
                source_turn_id=source_turn_id,
                recommended_action=MemoryTriageAction.auto_save,
            )

        return None

    def extract_preferences(self, text: str) -> list[str]:
        candidate = self.extract_one(text)
        if candidate is None or candidate.candidate_type != CandidateType.interest:
            return []
        return [candidate.summary]
