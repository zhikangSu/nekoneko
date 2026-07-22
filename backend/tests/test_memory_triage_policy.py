from app.schemas.memory import MemoryCategory, MemoryEntry
from app.schemas.memory_candidate import MemoryTriageAction
from app.schemas.memory_card import CandidateType
from app.tools.memory_candidate_extractor import MemoryCandidateExtractor
from app.tools.memory_triage_policy import MemoryTriagePolicy


def _candidate(text: str):
    candidate = MemoryCandidateExtractor().extract_one(text, "t1")
    assert candidate is not None
    return candidate


def _memory(content: str) -> MemoryEntry:
    return MemoryEntry(
        id="m_1",
        user_id="u",
        category=MemoryCategory.profile_preference,
        content=content,
        created_at="2026-07-08T00:00:00+00:00",
    )


def test_interest_auto_saves_without_asking():
    decision = MemoryTriagePolicy().decide(
        _candidate("我喜欢粤剧"), existing_memories=[]
    )
    assert decision.action == MemoryTriageAction.auto_save
    assert decision.ask_now is False


def test_fact_creates_authorized_card():
    decision = MemoryTriagePolicy().decide(
        _candidate("我年轻时做过教师"), existing_memories=[]
    )
    assert decision.action == MemoryTriageAction.create_card
    assert decision.ask_now is True


def test_boundary_creates_boundary_card():
    candidate = _candidate("我不想再聊老伴去世的事")
    decision = MemoryTriagePolicy().decide(candidate, existing_memories=[])
    assert candidate.candidate_type == CandidateType.boundary_preference
    assert decision.action == MemoryTriageAction.create_boundary_card
    assert decision.ask_now is True


def test_sensitive_content_is_ignored_by_default():
    decision = MemoryTriagePolicy().decide(
        _candidate("老伴去世以后我一个人住"), existing_memories=[]
    )
    assert decision.action == MemoryTriageAction.ignore
    assert decision.ask_now is False


def test_duplicate_existing_memory_is_ignored_with_duplicate_reason():
    decision = MemoryTriagePolicy().decide(
        _candidate("我爱听粤剧"),
        existing_memories=[_memory("喜欢粤剧")],
    )
    assert decision.action == MemoryTriageAction.ignore
    assert decision.cooldown_applied is True
    assert "重复" in decision.reason
    assert decision.target_memory_id == "m_1"


def test_near_duplicate_updates_existing_memory():
    decision = MemoryTriagePolicy().decide(
        _candidate("我喜欢太极拳"),
        existing_memories=[_memory("喜欢太极")],
    )
    assert decision.action == MemoryTriageAction.update_existing
    assert decision.cooldown_applied is True
    assert decision.target_memory_id == "m_1"


def test_distinct_interest_with_shared_prefix_is_saved():
    decision = MemoryTriagePolicy().decide(
        _candidate("我特别喜欢书法"),
        existing_memories=[_memory("喜欢书")],
    )
    assert decision.action == MemoryTriageAction.auto_save
    assert decision.target_memory_id is None


def test_distinct_longer_interest_is_saved():
    decision = MemoryTriagePolicy().decide(
        _candidate("我喜欢粤剧折子戏"),
        existing_memories=[_memory("喜欢粤剧")],
    )
    assert decision.action == MemoryTriageAction.auto_save
    assert decision.target_memory_id is None
