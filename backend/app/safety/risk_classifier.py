"""Deterministic risk classification used by InputRuleGuard (issue #8)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.core.constants import RiskLevel
from app.safety.risk_keywords import RISK_CATEGORIES, RiskCategory


@dataclass
class RiskClassification:
    level: RiskLevel = RiskLevel.low
    category: Optional[str] = None
    template: Optional[str] = None
    matched_terms: list[str] = field(default_factory=list)

    @property
    def is_risky(self) -> bool:
        return self.level in (RiskLevel.high, RiskLevel.crisis)


def classify_risk(text: str) -> RiskClassification:
    """Return the most severe matching category (crisis before high)."""
    haystack = text or ""
    for category in RISK_CATEGORIES:  # ordered most-severe first
        matched = [kw for kw in category.keywords if kw in haystack]
        if matched:
            return _classification_for(category, matched)
    return RiskClassification()


def _classification_for(
    category: RiskCategory, matched: list[str]
) -> RiskClassification:
    return RiskClassification(
        level=category.level,
        category=category.key,
        template=category.template,
        matched_terms=matched,
    )
