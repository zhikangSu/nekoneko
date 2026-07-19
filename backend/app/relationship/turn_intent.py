"""Small deterministic classifiers for conversational turn shape."""

from __future__ import annotations

from typing import Literal

from app.relationship.topic_classifier import Topic
from app.schemas.relationship import InteractionIntent

PresenceQuestionKind = Literal["activity", "identity", "hearing"]

_PRESENCE_QUESTION_MARKERS: dict[PresenceQuestionKind, tuple[str, ...]] = {
    "hearing": (
        "能听见吗",
        "听得见吗",
        "听到我说话吗",
        "听见我说话吗",
        "你们能听到吗",
        "你能听到吗",
    ),
    "identity": (
        "你们是谁",
        "你是谁",
        "你们是什么",
        "你是什么",
    ),
    "activity": (
        "你们在干什么",
        "你们在做什么",
        "你在干什么",
        "你在做什么",
        "你们刚才在聊什么",
        "你们聊什么",
        "在干嘛",
        "在做啥",
    ),
}

_PRESENCE_REPLY_MARKERS: dict[PresenceQuestionKind, tuple[str, ...]] = {
    "activity": (
        "在陪",
        "在和",
        "在聊",
        "正陪",
        "正和",
        "正聊",
        "等您",
        "等着您",
        "刚才聊",
        "陪您聊天",
        "陪您说话",
        "陪着您",
        "在这里",
        "在听",
    ),
    "identity": ("我是", "我们是", "叫", "陪伴 ai", "陪伴ai"),
    "hearing": ("听见", "听到", "听得见", "在听"),
}


def classify_presence_question(text: str) -> PresenceQuestionKind | None:
    """Classify direct questions about the companion's presence or activity."""

    normalized = text.strip().lower()
    for kind, markers in _PRESENCE_QUESTION_MARKERS.items():
        if any(marker in normalized for marker in markers):
            return kind
    return None


def classify_interaction_intent(text: str, topic: Topic) -> InteractionIntent:
    """Classify turn shape independently from the reminiscence topic bucket.

    ``Topic.other`` means only that the current utterance did not introduce one
    of the study's reminiscence topics. It must not be interpreted as permission
    to start a generic reminiscence interview.
    """

    presence_kind = classify_presence_question(text)
    if presence_kind is not None:
        return InteractionIntent(f"presence_{presence_kind}")
    if topic is not Topic.other:
        return InteractionIntent.topic_turn
    return InteractionIntent.general_turn


def presence_reply_matches(text: str, kind: PresenceQuestionKind) -> bool:
    """Return whether a reply directly answers the detected presence question."""

    normalized = text.strip().lower()
    return any(marker in normalized for marker in _PRESENCE_REPLY_MARKERS[kind])
