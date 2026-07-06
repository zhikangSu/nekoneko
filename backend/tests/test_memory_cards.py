"""Tests for the authorized Memory Card workflow (issue #54).

Covers the rule-based classifier, the four-action apply semantics against a real
``MemoryStore``, the sensitive-content safety rule (never auto-saved), and an
end-to-end pass through the three REST endpoints. All offline / no LLM.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_memory_card_store, get_memory_store
from app.main import app
from app.schemas.memory import MemoryCategory
from app.schemas.memory_card import (
    CandidateType,
    CardAction,
    CardStatus,
    DefaultAction,
    Sensitivity,
)
from app.stores.memory_card_store import MemoryCardStore
from app.stores.memory_store import MemoryStore
from app.tools.memory_card_tool import MemoryCardTool


@pytest.fixture
def memory_store(tmp_path) -> MemoryStore:
    return MemoryStore(tmp_path / "memory")


@pytest.fixture
def tool(memory_store) -> MemoryCardTool:
    return MemoryCardTool(memory_store)


# --- classifier / drafting ---------------------------------------------------


def test_fact_card(tool):
    card = tool.draft_from_text("u1", "我年轻时做过教师")
    assert card is not None
    assert card.candidate_type == CandidateType.fact
    assert card.default_action == DefaultAction.confirm_before_save
    assert card.sensitivity in (Sensitivity.low, Sensitivity.medium)
    assert card.status == CardStatus.pending


def test_interest_card(tool):
    card = tool.draft_from_text("u1", "我喜欢粤剧")
    assert card is not None
    assert card.candidate_type == CandidateType.interest
    assert card.default_action == DefaultAction.suggest_save
    assert card.summary == "喜欢粤剧"
    assert card.sensitivity == Sensitivity.low


def test_emotion_card(tool):
    card = tool.draft_from_text("u1", "我年轻时得过奖，特别自豪")
    # 情感优先于 fact? No — fact has higher priority than emotion, and this text
    # also matches fact via 「我年轻时…」. Use a clean emotion-only utterance.
    card = tool.draft_from_text("u1", "想起那次旅行我很想念")
    assert card is not None
    assert card.candidate_type == CandidateType.emotion
    assert card.sensitivity == Sensitivity.medium
    assert card.default_action == DefaultAction.confirm_before_save


def test_sensitive_card_not_auto_saved(tool, memory_store):
    card = tool.draft_from_text("u1", "老伴去世以后我一个人住")
    assert card is not None
    assert card.candidate_type == CandidateType.sensitive
    assert card.sensitivity == Sensitivity.high
    assert card.default_action == DefaultAction.do_not_save_by_default
    # Drafting alone must NEVER write anything to long-term memory.
    assert memory_store.list("u1") == []


def test_boundary_beats_sensitive(tool):
    # 「我不想再聊老伴去世的事」 → boundary_preference (a boundary), NOT sensitive.
    card = tool.draft_from_text("u1", "我不想再聊老伴去世的事")
    assert card is not None
    assert card.candidate_type == CandidateType.boundary_preference
    assert card.sensitivity == Sensitivity.medium


def test_boundary_bie_ti(tool):
    card = tool.draft_from_text("u1", "以后别提我儿子")
    assert card is not None
    assert card.candidate_type == CandidateType.boundary_preference


def test_no_candidate_returns_none(tool):
    assert tool.draft_from_text("u1", "今天天气怎么样") is None
    assert tool.draft_from_text("u1", "") is None


# --- apply_action semantics --------------------------------------------------


def test_action_save_writes_memory(tool, memory_store):
    card = tool.draft_from_text("u1", "我喜欢粤剧")
    updated = tool.apply_action(card, CardAction.save, None, memory_store)
    assert updated.status == CardStatus.saved
    mems = memory_store.list("u1")
    assert len(mems) == 1
    assert mems[0].category == MemoryCategory.profile_preference
    assert "粤剧" in mems[0].content


def test_action_edit_then_save(tool, memory_store):
    card = tool.draft_from_text("u1", "我年轻时做过教师")
    updated = tool.apply_action(
        card, CardAction.edit_then_save, "年轻时在乡村小学当老师", memory_store
    )
    assert updated.status == CardStatus.edited_saved
    assert updated.summary == "年轻时在乡村小学当老师"
    mems = memory_store.list("u1")
    assert len(mems) == 1
    assert mems[0].category == MemoryCategory.event_memory
    assert mems[0].content == "年轻时在乡村小学当老师"


def test_action_edit_then_save_requires_summary(tool, memory_store):
    card = tool.draft_from_text("u1", "我喜欢粤剧")
    with pytest.raises(ValueError):
        tool.apply_action(card, CardAction.edit_then_save, "   ", memory_store)


def test_action_reject_writes_nothing(tool, memory_store):
    card = tool.draft_from_text("u1", "我喜欢粤剧")
    updated = tool.apply_action(card, CardAction.reject, None, memory_store)
    assert updated.status == CardStatus.rejected
    assert memory_store.list("u1") == []


def test_action_never_mention_writes_boundary(tool, memory_store):
    card = tool.draft_from_text("u1", "我喜欢粤剧")
    updated = tool.apply_action(card, CardAction.never_mention, None, memory_store)
    assert updated.status == CardStatus.never_mention
    mems = memory_store.list("u1")
    assert len(mems) == 1
    # Written as a boundary preference, phrased as an avoid-rule — NOT a normal
    # profile/event memory.
    assert mems[0].category == MemoryCategory.boundary_preference
    assert "不要再提" in mems[0].content
    assert mems[0].category != MemoryCategory.profile_preference


def test_sensitive_save_only_on_explicit_action(tool, memory_store):
    card = tool.draft_from_text("u1", "老伴去世以后我一个人住")
    # Still nothing until the user acts.
    assert memory_store.list("u1") == []
    updated = tool.apply_action(card, CardAction.save, None, memory_store)
    assert updated.status == CardStatus.saved
    mems = memory_store.list("u1")
    assert len(mems) == 1
    assert mems[0].category == MemoryCategory.event_memory


def test_boundary_save_category(tool, memory_store):
    card = tool.draft_from_text("u1", "我不想再聊老伴去世的事")
    updated = tool.apply_action(card, CardAction.save, None, memory_store)
    assert updated.status == CardStatus.saved
    mems = memory_store.list("u1")
    assert len(mems) == 1
    assert mems[0].category == MemoryCategory.boundary_preference


# --- end-to-end REST ---------------------------------------------------------


@pytest.fixture
def card_client(tmp_path):
    mem = MemoryStore(tmp_path / "memory")
    cards = MemoryCardStore(tmp_path / "cards")
    app.dependency_overrides[get_memory_store] = lambda: mem
    app.dependency_overrides[get_memory_card_store] = lambda: cards
    client = TestClient(app)
    client._mem = mem  # type: ignore[attr-defined]
    yield client
    app.dependency_overrides.clear()


def test_e2e_draft_list_save(card_client):
    uid = "e2e_user"

    # 1) draft a card
    draft = card_client.post(
        f"/api/memory-cards/{uid}/draft", json={"text": "我年轻时做过教师"}
    )
    assert draft.status_code == 201
    card = draft.json()
    assert card["candidate_type"] == "fact"
    assert card["default_action"] == "confirm_before_save"
    assert card["status"] == "pending"
    card_id = card["card_id"]

    # 2) list pending cards
    listed = card_client.get(f"/api/memory-cards/{uid}", params={"status": "pending"})
    assert listed.status_code == 200
    body = listed.json()
    assert body["user_id"] == uid
    assert any(c["card_id"] == card_id for c in body["cards"])

    # 3) save → written to long-term memory, status updated
    acted = card_client.post(
        f"/api/memory-cards/{uid}/{card_id}/action", json={"action": "save"}
    )
    assert acted.status_code == 200
    assert acted.json()["status"] == "saved"

    mem = card_client._mem  # type: ignore[attr-defined]
    assert any("教师" in m.content for m in mem.list(uid))
    # no longer pending
    pending = card_client.get(
        f"/api/memory-cards/{uid}", params={"status": "pending"}
    ).json()
    assert not any(c["card_id"] == card_id for c in pending["cards"])


def test_e2e_no_candidate_returns_204(card_client):
    resp = card_client.post(
        "/api/memory-cards/e2e_user/draft", json={"text": "今天天气怎么样"}
    )
    assert resp.status_code == 204


def test_e2e_reject_writes_nothing(card_client):
    uid = "e2e_reject"
    card_id = card_client.post(
        f"/api/memory-cards/{uid}/draft", json={"text": "我喜欢粤剧"}
    ).json()["card_id"]
    acted = card_client.post(
        f"/api/memory-cards/{uid}/{card_id}/action", json={"action": "reject"}
    )
    assert acted.status_code == 200
    assert acted.json()["status"] == "rejected"
    assert card_client._mem.list(uid) == []  # type: ignore[attr-defined]


def test_e2e_never_mention_writes_boundary(card_client):
    uid = "e2e_never"
    card_id = card_client.post(
        f"/api/memory-cards/{uid}/draft", json={"text": "我喜欢粤剧"}
    ).json()["card_id"]
    acted = card_client.post(
        f"/api/memory-cards/{uid}/{card_id}/action",
        json={"action": "never_mention"},
    )
    assert acted.status_code == 200
    assert acted.json()["status"] == "never_mention"
    mems = card_client._mem.list(uid)  # type: ignore[attr-defined]
    assert len(mems) == 1
    assert mems[0].category == MemoryCategory.boundary_preference


def test_e2e_action_on_missing_card_404(card_client):
    resp = card_client.post(
        "/api/memory-cards/e2e_user/mc_missing/action", json={"action": "save"}
    )
    assert resp.status_code == 404


def test_e2e_double_action_is_rejected_409(card_client):
    """A card is single-use: re-acting on a resolved card returns 409 and never
    writes the same memory twice (guards double-clicks / retries)."""
    uid = "e2e_idem"
    card_id = card_client.post(
        f"/api/memory-cards/{uid}/draft", json={"text": "我喜欢粤剧"}
    ).json()["card_id"]
    first = card_client.post(
        f"/api/memory-cards/{uid}/{card_id}/action", json={"action": "save"}
    )
    assert first.status_code == 200
    second = card_client.post(
        f"/api/memory-cards/{uid}/{card_id}/action", json={"action": "save"}
    )
    assert second.status_code == 409
    mem = card_client._mem  # type: ignore[attr-defined]
    assert len([m for m in mem.list(uid) if "粤剧" in m.content]) == 1


def test_boundary_keyword_fallback_summary_not_doubled(tool):
    """A boundary phrase that names no clean object keeps the user's own wording
    (no '不想再聊我不想再聊' double-prefix)."""
    card = tool.draft_from_text("u", "我不想再聊")
    assert card is not None
    assert card.candidate_type == CandidateType.boundary_preference
    assert card.summary == "我不想再聊"


def test_boundary_with_object_keeps_clean_summary(tool):
    card = tool.draft_from_text("u", "我不想再聊老伴去世的事")
    assert card is not None
    assert card.candidate_type == CandidateType.boundary_preference
    assert card.summary == "不想再聊老伴去世的事"
