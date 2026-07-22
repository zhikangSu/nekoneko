"""Deterministic, offline stand-in for a real LLM (DEMO_MODE default).

The replies are warm, concise, and **safe by construction**: they are fixed
templates that never contain diagnosis, medication, or dosage content, and they
never echo arbitrary user text back. This is a Slice-1 baseline, not a safety
system — real risk routing arrives with InputRuleGuard / SafetyCriticAgent (#8).
"""

from __future__ import annotations

from app.core.constants import CompanionMode
from app.relationship.turn_intent import classify_presence_question
from app.services.llm_provider import CompanionReplyInput, LLMProvider

# role_first: emotional grounding without mechanically appending a question.
_ROLE_FIRST_REPLIES = (
    "我在的。先按您刚才说的来，不着急往下问。",
    "嗯，我听到了。您想继续时再慢慢说，想换个话题也可以。",
    "我在听着。先把您刚才的意思接住，不催您继续。",
)

# neutral_assistant: still warm and kind, a little more direct.
_NEUTRAL_REPLIES = (
    "好的，我明白了。先按您刚才说的处理。",
    "我听到了。我们可以按最直接的一步慢慢来。",
    "知道了，谢谢您告诉我。我先不额外追问。",
)

_FOLLOW_UP_MARKERS = (
    "刚才",
    "继续",
    "接着",
    "上一句",
    "前面",
    "这个话题",
    "你刚说",
)

_SENSITIVE_TOPIC_CARD_OPENINGS = {
    "deceased_grief": (
        "可以，我们聊聊已故亲友和回忆。这个话题有时会牵动不同感受，"
        "您可以按舒服的节奏说，也可以随时停下或换个话题。"
    ),
    "health_care": (
        "可以，我们聊聊身体健康和照护。我不能判断病情，也不能给用药或剂量建议；"
        "您可以从自己最想说的一点开始，也可以随时停下或换个话题。"
    ),
}


class FakeLLMProvider(LLMProvider):
    name = "fake"

    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        presence_kind = classify_presence_question(payload.message)
        if presence_kind == "activity":
            return "我们刚才在聊天，也在这里等您说话。您想问什么都可以直接问。"
        if presence_kind == "identity":
            return "我是您命名的 AI 陪伴伙伴，不是真实的人；现在正在这里陪您聊天。"
        if presence_kind == "hearing":
            return "听得见，我正在认真听您说话。"

        # Retrieval turn: surface the external fact warmly (a real LLM would
        # rewrite it; the fake provider wraps it in a gentle template).
        if payload.retrieval_context:
            return (
                f"我帮您看了一下：{payload.retrieval_context}"
                "您要是想出门，我可以帮您一起看看怎么安排，比如提醒您带把伞或带点水。"
            )

        if payload.topic in _SENSITIVE_TOPIC_CARD_OPENINGS:
            return _SENSITIVE_TOPIC_CARD_OPENINGS[payload.topic]

        if payload.conversation_history and any(
            marker in payload.message for marker in _FOLLOW_UP_MARKERS
        ):
            return (
                "我记得您刚才已经说过前面的那件事了。"
                "我们可以接着刚才的话慢慢聊，不用重新开始。"
            )

        replies = (
            _ROLE_FIRST_REPLIES
            if payload.mode == CompanionMode.role_first
            else _NEUTRAL_REPLIES
        )
        # Deterministic choice (no randomness): stable per message text.
        index = sum(ord(ch) for ch in payload.message) % len(replies)
        return replies[index]
