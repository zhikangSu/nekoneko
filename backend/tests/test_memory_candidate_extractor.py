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


def test_self_doubt_question_is_not_fact():
    assert MemoryCandidateExtractor().extract_one("我是不是老糊涂了") is None


def test_uncertain_question_is_not_fact():
    assert MemoryCandidateExtractor().extract_one("我是不是说错话了") is None


def test_question_particle_blocks_fact():
    assert MemoryCandidateExtractor().extract_one("我是苏州人吗") is None


def test_question_mark_blocks_interest():
    assert MemoryCandidateExtractor().extract_one("我喜欢听粤剧？") is None


def test_how_and_why_questions_produce_no_candidate():
    assert MemoryCandidateExtractor().extract_one("我怎么老是忘事呢") is None
    assert MemoryCandidateExtractor().extract_one("为什么我总是记不住") is None


def test_plain_fact_still_extracted():
    candidate = MemoryCandidateExtractor().extract_one("我是苏州人")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.fact
    assert candidate.summary == "我是苏州人"


def test_plain_interest_still_extracted_after_question_gate():
    candidate = MemoryCandidateExtractor().extract_one("我喜欢听粤剧")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.interest
    assert candidate.summary == "喜欢听粤剧"


def test_boundary_with_question_word_still_extracted():
    candidate = MemoryCandidateExtractor().extract_one("不要再问我子女的事")
    assert candidate is not None
    assert candidate.candidate_type == CandidateType.boundary_preference
