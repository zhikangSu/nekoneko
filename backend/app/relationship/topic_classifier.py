"""Rule-based reminiscence topic classifier (issue #52).

Keyword-first, deterministic, NO LLM. Given an older adult's utterance, it maps
the text to one of the Study-1 reminiscence topics (T01–T12, folded into the
``Topic`` enum below) so the RelationshipOrchestratorAgent can schedule the
right visible relationship roles.

Matching rules:

* Keyword-first: each topic owns a keyword list.
* Longest / most-specific keyword match wins, so a specific hit like
  "老照片" beats a generic hit like "以前".
* Sensitive keywords take priority: if any sensitive topic (grief / health /
  privacy-conflict) is mentioned at all, it outranks non-sensitive topics even
  when a non-sensitive keyword is longer. Sensitive framing must not be diluted
  by a cheerful co-occurring keyword.

This module only classifies; it does not decide roles or touch any existing
graph/safety/Guardian/Reminder/Retrieval path.
"""

from __future__ import annotations

from enum import Enum


class Topic(str, Enum):
    """Reminiscence topic buckets (Study-1 topic cards, folded)."""

    old_object_photo = "old_object_photo"  # 旧物 / 老照片 / 老电视
    work_collective = "work_collective"  # 工作 / 工厂 / 车间 / 集体 / 大院
    family_education = "family_education"  # 家庭 / 孩子 / 教育 / 儿女 / 孙
    culture_arts = "culture_arts"  # 戏曲 / 粤剧 / 老电影 / 老歌 / 地方文化
    deceased_grief = "deceased_grief"  # 老伴走了 / 去世 / 故人
    health_care = "health_care"  # 身体 / 生病 / 住院 / 吃药 / 健康
    privacy_family_conflict = "privacy_family_conflict"  # 家里闹 / 矛盾 / 隐私
    loneliness_mood = "loneliness_mood"  # 孤单 / 一个人 / 没意思
    general_reminiscence = "general_reminiscence"  # 想起以前 / 回忆
    other = "other"


# Topics that must be handled with restraint: no agent-agent persona banter,
# boundary_guardian leads, memory cards are never auto-generated.
SENSITIVE_TOPICS: frozenset[Topic] = frozenset(
    {
        Topic.deceased_grief,
        Topic.health_care,
        Topic.privacy_family_conflict,
    }
)


# Keyword tables. Ordering within a list does not matter; the classifier scores
# by the *length* of the matched keyword (longest/most-specific wins). Sensitive
# topics are checked first and win ties/overlaps.
_SENSITIVE_KEYWORDS: dict[Topic, tuple[str, ...]] = {
    Topic.deceased_grief: (
        "老伴走了",
        "老伴去世",
        "老伴不在了",
        "老伴",  # spouse in a reminiscence turn is treated as grief-sensitive
        "走了",  # euphemism for passing
        "去世",
        "过世",
        "离开",  # 离开了 / 离开的 / 离开我们
        "不在了",
        "故人",
        "先走一步",
        "遗像",
        "扫墓",
        "忌日",
    ),
    Topic.health_care: (
        "身体不好",
        "身体",
        "生病",
        "住院",
        "吃药",
        "药量",
        "剂量",
        "健康",
        "看病",
        "医院",
        "医生",
        "血压",
        "血糖",
        "心脏",
        "胸口痛",
        "摔倒",
        "手术",
    ),
    Topic.privacy_family_conflict: (
        "家里闹",
        "闹矛盾",
        "矛盾",
        "吵架",
        "隐私",
        "家丑",
        "不想让人知道",
        "别告诉",
        "私事",
        "闹翻",
        "断绝",
    ),
}

# Concrete/specific reminiscence topics. These take precedence over the generic
# fallback markers below: e.g. "看到老电视想起以前" is about the old TV
# (old_object_photo), not merely "以前" (general_reminiscence).
_CONCRETE_KEYWORDS: dict[Topic, tuple[str, ...]] = {
    Topic.old_object_photo: (
        "老照片",
        "旧照片",
        "老电视",
        "旧物",
        "老物件",
        "旧东西",
        "老唱片",
        "老收音机",
        "老家具",
        "老钟",
        "缝纫机",
    ),
    Topic.work_collective: (
        "上班",
        "工作",
        "工厂",
        "车间",
        "单位",
        "集体",
        "大院",
        "同事",
        "厂里",
        "生产队",
        "下乡",
        "值班",
        "老同事",
    ),
    Topic.family_education: (
        "家庭",
        "孩子",
        "教育",
        "儿女",
        "儿子",
        "女儿",
        "孙子",
        "孙女",
        "外孙",
        "带孩子",
        "养孩子",
        "上学",
        "读书",
    ),
    Topic.culture_arts: (
        "粤剧",
        "京剧",
        "戏曲",
        "唱戏",
        "老电影",
        "老歌",
        "地方文化",
        "评弹",
        "黄梅戏",
        "越剧",
        "样板戏",
        "曲艺",
    ),
}


# Generic fallback markers. Only consulted when no concrete topic matched, so a
# bare "以前" or "一个人" does not override a specific old-object/work/culture cue.
_FALLBACK_KEYWORDS: dict[Topic, tuple[str, ...]] = {
    Topic.loneliness_mood: (
        "孤单",
        "孤独",
        "一个人",
        "没意思",
        "没劲",
        "闷得慌",
        "空落落",
        "冷清",
        "寂寞",
    ),
    Topic.general_reminiscence: (
        "想起以前",
        "想起从前",
        "回忆",
        "回想",
        "以前",
        "从前",
        "那时候",
        "那会儿",
        "年轻的时候",
        "当年",
    ),
}


def _best_match(text: str, table: dict[Topic, tuple[str, ...]]) -> tuple[Topic | None, int]:
    """Return (best_topic, matched_keyword_length) for the given keyword table.

    Longest matched keyword wins. ``(None, 0)`` if nothing matches.
    """

    best_topic: Topic | None = None
    best_len = 0
    for topic, keywords in table.items():
        for kw in keywords:
            if kw in text and len(kw) > best_len:
                best_topic = topic
                best_len = len(kw)
    return best_topic, best_len


def classify_topic(text: str) -> Topic:
    """Classify an utterance into a :class:`Topic` (keyword-first, deterministic).

    Sensitive topics are checked first and take priority: if the text mentions
    grief / health / privacy-conflict at all, that wins even when a longer
    non-sensitive keyword co-occurs.
    """

    if not text or not text.strip():
        return Topic.other

    sensitive_topic, _sensitive_len = _best_match(text, _SENSITIVE_KEYWORDS)
    if sensitive_topic is not None:
        return sensitive_topic

    # Concrete/specific topics take precedence over generic reminiscence markers.
    concrete_topic, _concrete_len = _best_match(text, _CONCRETE_KEYWORDS)
    if concrete_topic is not None:
        return concrete_topic

    fallback_topic, _fallback_len = _best_match(text, _FALLBACK_KEYWORDS)
    if fallback_topic is not None:
        return fallback_topic

    return Topic.other
