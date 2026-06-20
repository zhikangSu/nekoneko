"""InfoRetrievalTool — controlled external retrieval (issue #13).

"Default no web" means: do not call web search / browser / external retrieval
unless the turn needs a time-sensitive external fact (weather, air quality, …).
It does NOT mean "no LLM" — companion language generation still uses the LLM
provider. In DEMO_MODE this returns deterministic mock facts; a real weather /
search provider is future work behind the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass

# Strong, standalone weather/air signals.
_WEATHER_KW = (
    "天气", "气温", "下雨", "会不会下雨", "出太阳", "紫外线", "冷不冷",
    "热不热", "要不要带伞",
)
_AIR_KW = ("空气质量", "空气好", "雾霾", "pm2.5", "pm2", "污染", "aqi")
# Outdoor-activity words count as a weather query ONLY with a time/weather
# context, so companionship / reminiscence ("我喜欢散步" / "我年轻时每天散步")
# do not trigger retrieval, while "今天下午适合散步吗" still does.
_OUTDOOR_KW = ("散步", "出门", "出去", "走走", "遛弯")
_OUTDOOR_CONTEXT = (
    "今天", "明天", "下午", "上午", "早上", "晚上", "现在", "适合", "天气",
    "外面", "会不会", "气温",
)


def _query_kind(text: str) -> str:
    haystack = text or ""
    if any(k in haystack for k in _AIR_KW):
        return "air_quality"
    if any(k in haystack for k in _WEATHER_KW):
        return "weather"
    if any(o in haystack for o in _OUTDOOR_KW) and any(
        c in haystack for c in _OUTDOOR_CONTEXT
    ):
        return "weather"
    return "generic"


@dataclass
class RetrievalResult:
    found: bool
    summary: str
    source: str
    mock: bool
    query_kind: str


class InfoRetrievalTool:
    name = "InfoRetrievalTool"

    def __init__(self, provider: str = "mock"):
        self.provider = provider

    @staticmethod
    def is_retrieval_query(text: str) -> bool:
        """True only for time-sensitive external facts (weather / air quality).

        Emotional disclosure, reminiscence, reminders, and memory chat are NOT
        retrieval queries — an outdoor word alone (散步/出门) does not count.
        """
        return _query_kind(text) != "generic"

    def retrieve(self, query: str) -> RetrievalResult:
        # DEMO_MODE: deterministic mock facts, never a real web call.
        kind = _query_kind(query)
        mock = self.provider == "mock"
        if kind == "air_quality":
            return RetrievalResult(
                found=True,
                summary="今天空气质量良好（AQI 约 60），适合短时间户外活动。",
                source="mock_air_quality",
                mock=mock,
                query_kind="air_quality",
            )
        if kind == "weather":
            return RetrievalResult(
                found=True,
                summary="今天下午多云，气温约 22°C，微风，没有降雨，比较适合出门走走。",
                source="mock_weather",
                mock=mock,
                query_kind="weather",
            )
        return RetrievalResult(
            found=False,
            summary="暂时没有查到相关的实时信息。",
            source="mock",
            mock=mock,
            query_kind="generic",
        )
