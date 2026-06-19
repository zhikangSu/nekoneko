"""Deterministic high-risk keyword catalog (issue #8).

Cheap, always-on signal for InputRuleGuard. Each category maps to a risk level
and the safety template used to respond. Keywords cover the examples in
AGENTS.md §9 / CLAUDE.md §9; this is intentionally a recall-first keyword list,
not a classifier that claims to understand meaning.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import RiskLevel


@dataclass(frozen=True)
class RiskCategory:
    key: str
    level: RiskLevel
    template: str  # template filename under safety/templates/
    keywords: tuple[str, ...]


# Order matters: the classifier returns the first (most severe) category that
# matches, so crisis categories are listed before high.
RISK_CATEGORIES: tuple[RiskCategory, ...] = (
    RiskCategory(
        key="emotional_crisis",
        level=RiskLevel.crisis,
        template="emotional_crisis_zh.md",
        keywords=(
            "自杀",
            "想死",
            "不想活",
            "不想活了",
            "活不下去",
            "活着没意思",
            "伤害自己",
            "结束生命",
        ),
    ),
    RiskCategory(
        key="fall_no_response",
        level=RiskLevel.crisis,
        template="fall_no_response_zh.md",
        keywords=(
            "摔倒",
            "摔了",
            "跌倒",
            "起不来",
            "站不起来",
            "爬不起来",
            "动不了",
        ),
    ),
    RiskCategory(
        key="emergency_help",
        level=RiskLevel.crisis,
        template="emergency_mock_zh.md",
        keywords=(
            "救命",
            "帮帮我",
            "快来人",
            "联系急救",
            "叫救护车",
            "打120",
            "打 120",
        ),
    ),
    RiskCategory(
        key="medical_symptom",
        level=RiskLevel.high,
        template="medical_symptom_zh.md",
        keywords=(
            "胸痛",
            "胸口痛",
            "胸口疼",
            "胸闷",
            "呼吸困难",
            "喘不上气",
            "喘不过气",
            "晕倒",
            "昏倒",
            "意识不清",
            "严重头晕",
            "心脏病",
            "中风",
        ),
    ),
    RiskCategory(
        key="medication",
        level=RiskLevel.high,
        template="medication_zh.md",
        keywords=(
            "吃两片",
            "吃几片",
            "多吃",
            "药吃多了",
            "吃多了药",
            "过量",
            "忘了吃药",
            "忘记吃药",
            "漏了药",
            "漏吃",
            "补吃",
            "补一片",
            "换药",
            "加药",
            "停药",
            "剂量",
        ),
    ),
)
