"""Short-term conversation history tests (#82)."""

from __future__ import annotations

from app.agents.companion import CompanionAgent
from app.core.constants import CompanionMode
from app.schemas.conversation import ConversationMessage
from app.services.llm_provider import CompanionReplyInput, LLMProvider
from app.services.xiaomimimo_llm_provider import XiaomiMiMoLLMProvider
from app.stores.conversation_history_store import ConversationHistoryStore


def test_follow_up_turn_uses_short_term_history_without_trace_content(client):
    uid = "history_followup_demo"
    first_text = "这件事让我想起以前"
    first = client.post(
        "/api/chat",
        json={"user_id": uid, "message": first_text},
    ).json()

    assert first["agent_trace"]["conversation_history_used"] is False
    assert first["agent_trace"]["conversation_history_count"] == 0

    second = client.post(
        "/api/chat",
        json={"user_id": uid, "message": "我们继续刚才的话题"},
    ).json()

    assert "接着刚才" in second["response_text"]
    assert second["agent_trace"]["conversation_history_used"] is True
    assert second["agent_trace"]["conversation_history_count"] == 2
    assert first_text not in str(second["agent_trace"])


def test_conversation_history_store_keeps_bounded_recent_window():
    store = ConversationHistoryStore(max_messages=4)
    for index in range(3):
        store.append_turn("u1", f"user {index}", f"assistant {index}")

    recent = store.recent("u1")

    assert len(recent) == 4
    assert [m.content for m in recent] == [
        "user 1",
        "assistant 1",
        "user 2",
        "assistant 2",
    ]


class _HistorySpyProvider(LLMProvider):
    name = "spy"

    def __init__(self) -> None:
        self.payloads: list[CompanionReplyInput] = []

    def generate_companion_reply(self, payload: CompanionReplyInput) -> str:
        self.payloads.append(payload)
        return "ok"


def test_companion_agent_passes_history_to_provider():
    provider = _HistorySpyProvider()
    agent = CompanionAgent(provider)
    history = [
        ConversationMessage(role="user", content="上一轮用户说的话"),
        ConversationMessage(role="assistant", content="上一轮回复"),
    ]

    agent.respond(
        message="继续刚才",
        mode=CompanionMode.role_first,
        companion_display_name=None,
        conversation_history=history,
    )

    assert provider.payloads[0].conversation_history == history


def test_xiaomimimo_provider_sends_history_before_current_user():
    provider = XiaomiMiMoLLMProvider.__new__(XiaomiMiMoLLMProvider)
    provider._model = "test-model"
    provider._temperature = 0.1
    provider._max_tokens = 128
    provider._generation_info = {}
    captured: dict = {}

    def fake_post(body: dict) -> dict:
        captured["body"] = body
        return {"choices": [{"message": {"content": "好的，我们接着聊。"}}]}

    provider._post = fake_post
    provider.generate_companion_reply(
        CompanionReplyInput(
            message="继续刚才",
            mode=CompanionMode.role_first,
            companion_display_name="陪伴 AI",
            system_prompt="system",
            conversation_history=[
                ConversationMessage(role="user", content="我刚才说的事"),
                ConversationMessage(role="assistant", content="我听到了"),
            ],
        )
    )

    messages = captured["body"]["messages"]
    assert [m["role"] for m in messages] == ["system", "user", "assistant", "user"]
    assert messages[1]["content"] == "我刚才说的事"
    assert messages[-1]["content"] == "继续刚才"
