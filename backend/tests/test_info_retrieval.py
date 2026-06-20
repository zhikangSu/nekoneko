from app.tools.info_retrieval import InfoRetrievalTool


def test_is_retrieval_query_for_weather_and_air():
    tool = InfoRetrievalTool()
    assert tool.is_retrieval_query("今天下午适合散步吗？") is True
    assert tool.is_retrieval_query("外面空气质量怎么样") is True


def test_is_not_retrieval_query_for_emotional_or_reminiscence():
    tool = InfoRetrievalTool()
    assert tool.is_retrieval_query("我今天有点孤单") is False
    assert tool.is_retrieval_query("我年轻时喜欢听粤剧") is False
    assert tool.is_retrieval_query("每天早上8点提醒我吃药") is False


def test_retrieve_weather():
    result = InfoRetrievalTool().retrieve("今天下午适合散步吗？")
    assert result.found is True
    assert result.query_kind == "weather"
    assert result.source == "mock_weather"
    assert result.mock is True


def test_retrieve_air_quality():
    result = InfoRetrievalTool().retrieve("今天空气质量怎么样")
    assert result.query_kind == "air_quality"


def test_retrieve_generic_not_found():
    result = InfoRetrievalTool().retrieve("你好呀")
    assert result.found is False
