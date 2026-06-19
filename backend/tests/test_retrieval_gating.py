"""Retrieval gating baseline (issue #5 boundary; full gating arrives in #13).

Companionship / emotional turns must not trigger external retrieval. No
retrieval tool exists yet, so the flag stays False for every turn; #13 adds the
weather/time-sensitive detection that may flip it.
"""


def test_emotional_turn_does_not_use_retrieval(client):
    body = client.post("/api/chat", json={"message": "我今天有点孤单"}).json()
    assert body["agent_trace"]["route"] == "companion_chat"
    assert body["agent_trace"]["retrieval_used"] is False


def test_reminiscence_turn_does_not_use_retrieval(client):
    body = client.post("/api/chat", json={"message": "我年轻的时候喜欢听粤剧"}).json()
    assert body["agent_trace"]["retrieval_used"] is False
