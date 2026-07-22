"""OutputRuleGuard — always-on, cheap check on the drafted reply (issue #8).

Defense in depth: even if a draft somehow contains medication/dosage specifics,
this guard rewrites it to a safe deflection before the reply leaves the system.
It also removes emoji and a small set of child-directed praise phrases that are
inappropriate for respectful older-adult companionship. Deterministic; no LLM
call.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Dosage/quantity-shaped patterns that must never appear in an outgoing reply.
_OUTPUT_VIOLATION_PATTERNS: tuple[str, ...] = (
    "毫克",
    "mg",
    "吃两片",
    "吃三片",
    "吃半片",
    "再吃一片",
    "加倍",
    "翻倍",
)

_SAFE_REWRITE = (
    "关于具体用药、剂量或要不要补吃，我不能给建议——这些请按医嘱，或咨询您的医生、药师。"
    "我可以帮您记一个吃药提醒，或记下想问医生的问题。"
)

_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001FAFF"
    "\u2600-\u27BF"
    "\uFE0F"
    "]"
)

_TONE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("您太乖了", "您这样安排很稳妥"),
    ("您真乖", "您这样安排很稳妥"),
    ("您太棒了", "听起来很不错"),
    ("您真棒", "听起来很不错"),
    ("小太阳", "温暖的存在"),
)


def _normalize_respectful_tone(text: str) -> tuple[str, list[str]]:
    normalized = text or ""
    adjustments: list[str] = []

    if _EMOJI_PATTERN.search(normalized):
        normalized = _EMOJI_PATTERN.sub("", normalized).replace("\u200d", "")
        adjustments.append("emoji")

    for source, replacement in _TONE_REPLACEMENTS:
        if source in normalized:
            normalized = normalized.replace(source, replacement)
            adjustments.append(source)

    if adjustments:
        normalized = re.sub(r"[ \t]{2,}", " ", normalized)
        normalized = re.sub(r"[ \t]+([，。！？；：])", r"\1", normalized)
        normalized = normalized.strip()

    return normalized, adjustments


@dataclass
class OutputGuardResult:
    passed: bool
    summary: str
    final_text: str
    rewritten: bool


class OutputRuleGuard:
    name = "OutputRuleGuard"

    def run(self, draft: str) -> OutputGuardResult:
        hits = [p for p in _OUTPUT_VIOLATION_PATTERNS if p in (draft or "")]
        if hits:
            return OutputGuardResult(
                passed=False,
                summary=f"输出命中用药/剂量措辞（{'、'.join(hits)}），已改写为安全话术",
                final_text=_SAFE_REWRITE,
                rewritten=True,
            )

        final_text, tone_adjustments = _normalize_respectful_tone(draft)
        if tone_adjustments:
            return OutputGuardResult(
                passed=True,
                summary=(
                    "输出已去除不适合长者陪伴的语气元素（"
                    f"{'、'.join(tone_adjustments)}）"
                ),
                final_text=final_text,
                rewritten=True,
            )

        return OutputGuardResult(
            passed=True,
            summary="输出无违规",
            final_text=draft,
            rewritten=False,
        )
