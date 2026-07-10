"""Memory triage traces keep metadata without persisting user utterances (#125)."""

import json

from fastapi.testclient import TestClient


def _chat(client: TestClient, user_id: str, message: str) -> dict:
    response = client.post("/api/chat", json={"user_id": user_id, "message": message})
    assert response.status_code == 200
    return response.json()


def _trace_record(client: TestClient, turn_id: str) -> dict:
    response = client.get(f"/api/traces/{turn_id}")
    assert response.status_code == 200
    return response.json()


def _memory_steps(trace: dict) -> list[dict]:
    return [step for step in trace["tools"] if step["kind"] == "memory"]


def _triage_step(trace: dict) -> dict:
    steps = [
        step for step in _memory_steps(trace) if step["name"] == "MemoryTriagePolicy"
    ]
    assert steps
    return steps[-1]


def _assert_raw_text_absent(trace: dict, raw_text: str) -> None:
    dumped = json.dumps(_memory_steps(trace), ensure_ascii=False)
    assert raw_text not in dumped


def test_sensitive_input_is_absent_from_response_and_persisted_memory_steps(client):
    raw_text = "老伴去世以后我一个人住"
    body = _chat(client, "trace_privacy_sensitive", raw_text)

    _assert_raw_text_absent(body["agent_trace"], raw_text)
    record = _trace_record(client, body["turn_id"])
    _assert_raw_text_absent(record["trace"], raw_text)

    triage = _triage_step(record["trace"])
    assert triage["detail"]["candidate_type"] == "sensitive"
    assert triage["detail"]["decision"]["action"] == "ignore"
    assert triage["detail"]["decision"]["reason"]
    assert "candidate" not in triage["detail"]
    assert "summary" not in triage["detail"]
    assert "evidence_text" not in triage["detail"]


def test_fact_and_emotion_traces_keep_only_candidate_metadata(client):
    cases = [
        ("trace_privacy_fact", "我年轻时做过教师", "fact"),
        ("trace_privacy_emotion", "把孩子们拉扯大是我最骄傲的事", "emotion"),
    ]

    for user_id, raw_text, candidate_type in cases:
        body = _chat(client, user_id, raw_text)
        record = _trace_record(client, body["turn_id"])
        _assert_raw_text_absent(body["agent_trace"], raw_text)
        _assert_raw_text_absent(record["trace"], raw_text)

        triage = _triage_step(record["trace"])
        assert triage["detail"]["candidate_type"] == candidate_type
        assert triage["detail"]["decision"]["action"] == "create_card"
        assert triage["detail"]["memory_card_id"]


def test_auto_saved_interest_trace_uses_id_and_keeps_saved_compatibility(client):
    raw_text = "我喜欢听粤剧"
    body = _chat(client, "trace_privacy_interest", raw_text)
    record = _trace_record(client, body["turn_id"])

    _assert_raw_text_absent(body["agent_trace"], raw_text)
    _assert_raw_text_absent(record["trace"], raw_text)

    triage = _triage_step(record["trace"])
    assert triage["detail"]["candidate_type"] == "interest"
    assert triage["detail"]["decision"]["action"] == "auto_save"
    assert triage["detail"]["saved"] is True
    assert triage["detail"]["saved_memory_id"]
    assert "candidate" not in triage["detail"]
