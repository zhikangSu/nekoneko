"""Deterministic, offline stand-in for a real LLM (DEMO_MODE default).

The replies are warm, concise, and **safe by construction**: they are fixed
templates that never contain diagnosis, medication, or dosage content, and they
never echo arbitrary user text back. This is a Slice-1 baseline, not a safety
system — real risk routing arrives with InputRuleGuard / SafetyCriticAgent (#8).
"""

from __future__ import annotations

from app.core.constants import CompanionMode
from app.services.llm_provider import CompanionReplyInput, LLMProvider

# role_first: emotional grounding first, then a gentle, optional follow-up.
_ROLE_FIRST_REPLIES = (
    "我在的。听您说这些，我想先陪您待一会儿。如果您愿意，可以慢慢和我多说说，现在心里是什么感觉？",
    "嗯，我听到了，谢谢您愿意告诉我。我们不着急，您想先从哪一件说起呢？",
    "我在听着。您愿意和我聊这些，我很珍惜。如果方便，您愿意再多讲一点吗？",
)

# neutral_assistant: still warm and kind, a little more direct.
_NEUTRAL_REPLIES = (
    "好的，我明白了。这件事我先记在心里，您还想补充些什么吗？",
    "我听到了。我们一起看看可以怎么做，您希望我先帮您做哪一步？",
    "知道了，谢谢您告诉我。您方便的话，可以再说说具体想怎么安排吗？",
)


class FakeLLMProvider(LLMProvider):
    name = "fake"

    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        replies = (
            _ROLE_FIRST_REPLIES
            if payload.mode == CompanionMode.role_first
            else _NEUTRAL_REPLIES
        )
        # Deterministic choice (no randomness): stable per message text.
        index = sum(ord(ch) for ch in payload.message) % len(replies)
        return replies[index]
