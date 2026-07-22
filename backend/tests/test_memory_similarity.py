from app.services.memory_similarity import MemorySimilarityService


def test_short_prefix_containment_is_not_similar():
    svc = MemorySimilarityService()
    assert svc.is_similar("喜欢书", "喜欢书法") is False
    assert svc.is_similar("喜欢粤剧", "喜欢粤剧折子戏") is False


def test_normalized_equal_is_duplicate():
    svc = MemorySimilarityService()
    assert svc.is_similar("喜欢听粤剧", "喜欢粤剧") is True
    assert svc.is_duplicate("喜欢听粤剧", "喜欢粤剧") is True
    assert svc.is_duplicate("喜欢粤剧", "喜欢粤剧") is True


def test_close_length_containment_is_similar_but_not_duplicate():
    svc = MemorySimilarityService()
    assert svc.is_similar("喜欢太极", "喜欢太极拳") is True
    assert svc.is_duplicate("喜欢太极", "喜欢太极拳") is False


def test_empty_text_is_not_similar():
    svc = MemorySimilarityService()
    assert svc.is_similar("", "喜欢书法") is False
    assert svc.is_duplicate("", "") is False
