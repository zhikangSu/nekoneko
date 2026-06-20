"""Deterministic risk classification used by InputRuleGuard (issue #8)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from app.core.constants import RiskLevel
from app.safety.risk_keywords import RISK_CATEGORIES, RiskCategory

# Dosage-shaped phrasing the keyword list may miss, e.g. 「补两片」「多吃三颗」.
# Routes to the medication category so dosage questions never reach retrieval.
_DOSAGE_RE = re.compile(r"(补|吃|加|再吃|多吃|少吃)\s*[一二两三四五六七八九十\d]+\s*[片颗粒丸]")
_MEDICATION_CATEGORY = next(c for c in RISK_CATEGORIES if c.key == "medication")


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
    dosage = _DOSAGE_RE.search(haystack)
    if dosage:
        return _classification_for(_MEDICATION_CATEGORY, [dosage.group(0)])
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
