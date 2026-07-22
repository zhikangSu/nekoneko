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


def test_conversation_history_is_scoped_by_study_session(client):
    uid = "history_session_scope_demo"
    upper_session = "ambient_opera_demo"
    lower_session = "main_topic_demo"
    first_text = "我刚才在上面的聊天场聊了越剧"

    first = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": first_text,
            "study_session_id": upper_session,
        },
    ).json()
    assert first["agent_trace"]["conversation_history_count"] == 0

    lower = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "我们继续刚才的话题",
            "study_session_id": lower_session,
            "topic_id": "T02",
            "topic_label": "年轻时的工作经历",
            "material_type": "topic_card",
        },
    ).json()
    assert lower["agent_trace"]["conversation_history_used"] is False
    assert lower["agent_trace"]["conversation_history_count"] == 0
    assert "越剧" not in lower["response_text"]

    upper_followup = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "我们继续刚才的话题",
            "study_session_id": upper_session,
        },
    ).json()
    assert upper_followup["agent_trace"]["conversation_history_used"] is True
    assert upper_followup["agent_trace"]["conversation_history_count"] == 2


def test_ambient_seed_is_used_once_without_overwriting_session_history(client):
    uid = "history_ambient_seed_demo"
    session_id = "ambient_seed_opera_demo"
    seed = [
        {"role": "assistant", "content": "中年传承者：刚才我们在聊粤剧和地方文化。"},
        {"role": "assistant", "content": "同龄共鸣者：有些唱段一响就很亲切。"},
    ]

    first = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "你们在干什么",
            "study_session_id": session_id,
            "conversation_seed": seed,
        },
    ).json()

    assert first["agent_trace"]["conversation_seed_used"] is True
    assert first["agent_trace"]["conversation_seed_count"] == 2
    assert first["agent_trace"]["conversation_history_used"] is True
    assert first["agent_trace"]["conversation_history_count"] == 2
    assert "在聊天" in first["response_text"]
    assert "粤剧" not in str(first["agent_trace"])

    second = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "继续刚才的话题",
            "study_session_id": session_id,
            "conversation_seed": seed,
        },
    ).json()

    assert second["agent_trace"]["conversation_seed_used"] is False
    assert second["agent_trace"]["conversation_seed_count"] == 0
    assert second["agent_trace"]["conversation_history_count"] == 4


def test_conversation_seed_is_scoped_by_study_session(client):
    uid = "history_seed_scope_demo"
    seed = [{"role": "assistant", "content": "同龄共鸣者：我们先聊两句。"}]

    first = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "你好",
            "study_session_id": "ambient_seed_a",
            "conversation_seed": seed,
        },
    ).json()
    second = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "你好",
            "study_session_id": "ambient_seed_b",
            "conversation_seed": seed,
        },
    ).json()

    assert first["agent_trace"]["conversation_seed_count"] == 1
    assert second["agent_trace"]["conversation_seed_count"] == 1


def test_session_only_scope_skips_long_term_memory(client):
    uid = "history_session_memory_scope_demo"
    saved = client.post(
        "/api/chat",
        json={"user_id": uid, "message": "我喜欢听粤剧"},
    ).json()
    assert any(step["detail"].get("saved") for step in saved["agent_trace"]["tools"])

    scoped = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "聊这个吧",
            "study_session_id": "ambient_work_demo",
            "memory_scope": "session_only",
            "topic_id": "T02",
            "topic_label": "年轻时的工作经历",
            "material_type": "topic_card",
        },
    ).json()

    assert scoped["agent_trace"]["memory_used"] is False
    assert any(
        step["detail"].get("memory_scope") == "session_only"
        for step in scoped["agent_trace"]["tools"]
    )


def test_ambient_like_session_still_saves_low_sensitivity_preference(client):
    uid = "history_ambient_memory_default_demo"
    body = client.post(
        "/api/chat",
        json={
            "user_id": uid,
            "message": "我喜欢听粤剧",
            "study_session_id": "ambient_memory_default_demo",
        },
    ).json()

    assert body["agent_trace"]["conversation_history_count"] == 0
    assert any(step["detail"].get("saved") for step in body["agent_trace"]["tools"])

    stored = client.get(f"/api/memory/{uid}").json()
    assert any("粤剧" in memory["content"] for memory in stored["memories"])


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


def test_conversation_history_store_seeds_only_an_empty_session():
    store = ConversationHistoryStore(max_messages=4)
    seed = [
        ConversationMessage(role="assistant", content="场景开场一"),
        ConversationMessage(role="assistant", content="场景开场二"),
    ]

    assert store.seed_if_empty("u1", seed, "ambient") == 2
    assert store.seed_if_empty("u1", seed, "ambient") == 0
    assert [message.content for message in store.recent("u1", "ambient")] == [
        "场景开场一",
        "场景开场二",
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
