"""InputRuleGuard — always-on, cheap, deterministic risk check (issue #8).

Runs every turn before routing. It does not call an LLM. SafetyCriticAgent is
only invoked later when this guard flags risk (AGENTS.md §9).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.safety.risk_classifier import RiskClassification, classify_risk


@dataclass
class InputGuardResult:
    classification: RiskClassification
    passed: bool  # True when no high/crisis risk was found
    summary: str


class InputRuleGuard:
    name = "InputRuleGuard"

    def run(self, text: str) -> InputGuardResult:
        classification = classify_risk(text)
        passed = not classification.is_risky
        if passed:
            summary = "未发现高风险关键词"
        else:
            terms = "、".join(classification.matched_terms)
            summary = (
                f"命中 {classification.category}"
                f"（{classification.level.value}）：{terms}"
            )
        return InputGuardResult(classification=classification, passed=passed, summary=summary)
