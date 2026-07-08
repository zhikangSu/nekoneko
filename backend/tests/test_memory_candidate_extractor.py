from app.schemas.memory_card import CandidateType, Sensitivity
from app.tools.memory_candidate_extractor import MemoryCandidateExtractor


def test_extracts_low_sensitivity_interest():
    candidate = MemoryCandidateExtractor().extract_one("我喜欢听粤剧", "t1")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.interest
    assert candidate.summary == "喜欢听粤剧"
    assert candidate.sensitivity == Sensitivity.low
    assert candidate.source_turn_id == "t1"


def test_extracts_fact_experience():
    candidate = MemoryCandidateExtractor().extract_one("我年轻时做过教师")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.fact
    assert candidate.summary == "我年轻时做过教师"


def test_extracts_boundary_before_sensitive():
    candidate = MemoryCandidateExtractor().extract_one("我不想再聊老伴去世的事")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.boundary_preference
    assert candidate.summary == "不想再聊老伴去世的事"
    assert candidate.sensitivity == Sensitivity.medium


def test_extracts_role_preference():
    candidate = MemoryCandidateExtractor().extract_one("我更喜欢同龄人陪我聊")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.role_preference
    assert candidate.summary == "偏好同龄人陪聊"


def test_sensitive_candidate_is_high_sensitivity():
    candidate = MemoryCandidateExtractor().extract_one("老伴去世以后我一个人住")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.sensitive
    assert candidate.sensitivity == Sensitivity.high


def test_temporary_mood_is_not_long_term_candidate():
    assert MemoryCandidateExtractor().extract_one("我今天有点烦") is None
