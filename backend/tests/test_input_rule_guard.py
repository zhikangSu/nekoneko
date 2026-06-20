from app.core.constants import RiskLevel
from app.safety.risk_classifier import classify_risk
from app.tools.input_rule_guard import InputRuleGuard


def test_low_risk_for_normal_text():
    result = InputRuleGuard().run("今天天气不错，我想出去走走。")
    assert result.passed is True
    assert result.classification.level == RiskLevel.low
    assert result.classification.category is None


def test_medical_symptom_is_high():
    cls = classify_risk("我胸口痛，是不是心脏病？")
    assert cls.level == RiskLevel.high
    assert cls.category == "medical_symptom"
    assert cls.is_risky is True


def test_medication_is_high():
    cls = classify_risk("我忘了吃药，现在能不能吃两片？")
    assert cls.level == RiskLevel.high
    assert cls.category == "medication"


def test_emotional_crisis_is_crisis():
    cls = classify_risk("我不想活了。")
    assert cls.level == RiskLevel.crisis
    assert cls.category == "emotional_crisis"


def test_fall_is_crisis():
    cls = classify_risk("我摔倒了，起不来。")
    assert cls.level == RiskLevel.crisis
    assert cls.category == "fall_no_response"


def test_help_is_crisis():
    cls = classify_risk("救命，帮帮我。")
    assert cls.level == RiskLevel.crisis
    assert cls.category == "emergency_help"


def test_most_severe_category_wins():
    # Contains both a crisis term (想死) and a medication term (换药).
    cls = classify_risk("我想死，还要不要换药？")
    assert cls.level == RiskLevel.crisis
    assert cls.category == "emotional_crisis"


def test_dosage_phrasing_not_in_keywords_is_caught():
    # 「补两片」isn't a literal keyword but the dosage regex catches it (#13).
    for text in ("我能不能补两片药？", "要不要多吃三颗", "再吃两粒可以吗"):
        cls = classify_risk(text)
        assert cls.level == RiskLevel.high
        assert cls.category == "medication"
