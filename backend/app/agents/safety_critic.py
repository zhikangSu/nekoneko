"""SafetyCriticAgent — high-risk escalation path (issue #8).

Invoked **only** when InputRuleGuard flags risk (never on low-risk turns). It
reviews the flagged category and returns the matching safe template. In demo
mode this is deterministic (no LLM): the template is the safe, non-diagnostic,
non-dosage response that also makes clear no real emergency action is taken.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from app.core.constants import RiskLevel
from app.safety.risk_classifier import RiskClassification

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "safety" / "templates"
_FALLBACK_TEMPLATE = "emergency_mock_zh.md"


@lru_cache(maxsize=None)
def _load_template(name: str) -> str:
    path = _TEMPLATES_DIR / name
    if not path.exists():
        path = _TEMPLATES_DIR / _FALLBACK_TEMPLATE
    return path.read_text(encoding="utf-8").strip()


@dataclass
class SafetyResult:
    response_text: str
    template: str
    category: Optional[str]
    level: RiskLevel

    def trace_summary(self) -> str:
        return f"高风险升级：{self.category}（{self.level.value}）→ 安全模板 {self.template}"


class SafetyCriticAgent:
    name = "SafetyCriticAgent"

    def review(self, classification: RiskClassification) -> SafetyResult:
        template = classification.template or _FALLBACK_TEMPLATE
        return SafetyResult(
            response_text=_load_template(template),
            template=template,
            category=classification.category,
            level=classification.level,
        )
