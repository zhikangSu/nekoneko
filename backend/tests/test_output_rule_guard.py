from app.tools.output_rule_guard import OutputRuleGuard


def test_clean_output_passes_unchanged():
    text = "我在听着，您愿意多和我说说吗？"
    result = OutputRuleGuard().run(text)
    assert result.passed is True
    assert result.rewritten is False
    assert result.final_text == text


def test_dosage_like_output_is_rewritten():
    result = OutputRuleGuard().run("您可以吃两片试试。")
    assert result.passed is False
    assert result.rewritten is True
    assert "吃两片" not in result.final_text
    assert "按医嘱" in result.final_text


def test_unit_mention_is_rewritten():
    result = OutputRuleGuard().run("建议加到 500 毫克。")
    assert result.rewritten is True
    assert "毫克" not in result.final_text
