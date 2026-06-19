"""OutputRuleGuard — always-on, cheap check on the drafted reply (issue #8).

Defense in depth: even if a draft somehow contains medication/dosage specifics,
this guard rewrites it to a safe deflection before the reply leaves the system.
Deterministic; no LLM call.
"""

from __future__ import annotations

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
        if not hits:
            return OutputGuardResult(
                passed=True,
                summary="输出无违规",
                final_text=draft,
                rewritten=False,
            )
        return OutputGuardResult(
            passed=False,
            summary=f"输出命中用药/剂量措辞（{'、'.join(hits)}），已改写为安全话术",
            final_text=_SAFE_REWRITE,
            rewritten=True,
        )
