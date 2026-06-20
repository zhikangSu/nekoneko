"""End-to-end demo-scenario acceptance suite (issue #14).

One test per final-demo scenario in ``docs/demo_script.md``, driving the real
graph through the API in DEMO_MODE so the demo behaviors are locked as a
regression net. Per-feature unit coverage lives in the other test files; this
file asserts the *end-to-end* scenario: route + response + trace + side effects.

Everything runs offline (fake/mock providers, forced by conftest) — no real LLM,
ASR, TTS, web, phone, or caregiver call.
"""

from app.core.constants import (
    COMPANION_DISPLAY_NAME_FALLBACK_BILINGUAL,
    DEFAULT_COMPANION_DISPLAY_NAME,
)


# --- Demo 1: Companionship (emotional grounding first) -----------------------


def test_scenario_companionship(client):
    body = client.post(
        "/api/chat",
        json={"user_id": "demo_companion", "message": "我今天有点想老伴了。"},
    ).json()
    trace = body["agent_trace"]
    assert trace["route"] == "companion_chat"
    assert trace["risk_level"] == "low"
    # An emotional turn must not reach for web retrieval or the safety critic.
    assert trace["retrieval_used"] is False
    assert trace["safety_critic_used"] is False
    assert body["response_text"].strip()
    agents = [s["name"] for s in trace["agents"]]
    assert "CoordinatorAgent" in agents and "CompanionAgent" in agents
    guards = [s["name"] for s in trace["guards"]]
    assert "InputRuleGuard" in guards and "OutputRuleGuard" in guards


# --- Demo 2: Reminder (no dosage advice) ------------------------------------


def test_scenario_reminder_no_dosage(client):
    uid = "demo_reminder"
    body = client.post(
        "/api/chat", json={"user_id": uid, "message": "每天早上8点提醒我吃药"}
    ).json()
    assert body["agent_trace"]["route"] == "reminder_management"
    assert "08:00" in body["response_text"]
    assert "按医嘱" in body["response_text"]  # medication → defer to the doctor
    reminders = client.get(f"/api/reminders/{uid}").json()
    assert any(
        r["time"] == "08:00" and r["recurrence"] == "daily" for r in reminders
    )


# --- Demo 3: Memory (remember a preference, reuse it later) ------------------


def test_scenario_memory_remember_and_reuse(client):
    uid = "demo_memory"
    first = client.post(
        "/api/chat", json={"user_id": uid, "message": "我喜欢听粤剧"}
    ).json()
    assert any(s["detail"].get("saved") for s in first["agent_trace"]["tools"])
    stored = client.get(f"/api/memory/{uid}").json()
    assert any("粤剧" in m["content"] for m in stored["memories"])
    # A later, unrelated turn reads memory back (memory_used flips on).
    second = client.post(
        "/api/chat", json={"user_id": uid, "message": "今天有点无聊"}
    ).json()
    assert second["agent_trace"]["memory_used"] is True


# --- Demo 4: Proactive care (raw signal → StateEvent → Guardian) -------------


def test_scenario_proactive_care_boundary(client):
    body = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "demo_care", "preset_id": "poor_sleep"},
    ).json()
    # The boundary is explicit: SensorAdapter encodes raw → StateEvent, and the
    # GuardianAgent decides on the StateEvent (never the raw values).
    assert body["state_event"]["event_type"] == "POOR_SLEEP"
    assert body["guardian_decision"]["decision"] == "check_in"
    assert body["response_text"].strip()
    trace = body["agent_trace"]
    adapter = next(s for s in trace["tools"] if s["name"] == "SensorAdapter")
    assert adapter["kind"] == "tool"
    assert any(s["name"] == "GuardianAgent" for s in trace["agents"])
    assert trace["state_event"]["kind"] == "state_event"


# --- Demo 5: Controlled retrieval (weather yes / emotion no) -----------------


def test_scenario_controlled_retrieval(client):
    weather = client.post(
        "/api/chat", json={"user_id": "demo_retr", "message": "今天天气怎么样"}
    ).json()
    assert weather["agent_trace"]["route"] == "retrieval_supported_response"
    assert weather["agent_trace"]["retrieval_used"] is True
    # The same user disclosing a feeling must NOT trigger external retrieval.
    emotion = client.post(
        "/api/chat", json={"user_id": "demo_retr", "message": "我最近很孤单"}
    ).json()
    assert emotion["agent_trace"]["retrieval_used"] is False
    assert emotion["agent_trace"]["route"] == "companion_chat"


# --- Demo 6a: Safety — medication dosage interception -----------------------


def test_scenario_safety_medication_intercept(client):
    body = client.post(
        "/api/chat",
        json={"user_id": "demo_safe", "message": "我忘了吃药，现在能不能吃两片？"},
    ).json()
    trace = body["agent_trace"]
    assert trace["route"] == "safety_response"
    assert trace["safety_critic_used"] is True
    assert "按医嘱" in body["response_text"]
    for forbidden in ("两片", "毫克", "mg", "加倍", "多吃"):
        assert forbidden not in body["response_text"]


# --- Demo 6b: Safety — fall / no response → mock emergency -------------------


def test_scenario_safety_fall_emergency_mock(client):
    body = client.post(
        "/api/chat", json={"user_id": "demo_safe", "message": "我摔倒了，起不来"}
    ).json()
    trace = body["agent_trace"]
    assert trace["route"] == "emergency_mock"
    assert trace["risk_level"] == "crisis"
    assert "急救" in body["response_text"]
    assert "演示" in body["response_text"]  # explicit: no real call is placed


# --- Voice fallback: DEMO_MODE needs no key; chat is independent of voice ----


def test_scenario_voice_fallback_offline(client):
    asr = client.post(
        "/api/voice/asr", content=b"\x01" * 4096, headers={"content-type": "audio/wav"}
    ).json()
    assert asr["ok"] is True and asr["is_mock"] is True
    tts = client.post("/api/voice/tts", json={"text": "今天天气不错"}).json()
    assert tts["is_mock"] is True
    # Text chat still completes a turn regardless of the voice layer.
    chat = client.post("/api/chat", json={"message": "你好"})
    assert chat.status_code == 200 and chat.json()["response_text"].strip()


# --- Naming: neutral fallback, never a hardcoded invented persona name -------


def test_scenario_no_hardcoded_companion_name(client):
    assert DEFAULT_COMPANION_DISPLAY_NAME == "陪伴 AI"
    assert COMPANION_DISPLAY_NAME_FALLBACK_BILINGUAL == "陪伴 AI / AI Companion"
    # A brand-new user with no name set still gets a working turn via the fallback.
    body = client.post(
        "/api/chat", json={"user_id": "demo_unnamed", "message": "你好"}
    ).json()
    assert body["response_text"].strip()


# --- Trace distinguishes Agent / Tool / Guard / StateEvent / Retrieval -------


def test_scenario_trace_kind_distinctions(client):
    chat = client.post(
        "/api/chat", json={"user_id": "demo_trace", "message": "你好呀"}
    ).json()["agent_trace"]
    assert chat["agents"] and all(s["kind"] == "agent" for s in chat["agents"])
    assert chat["guards"] and all(s["kind"] == "guard" for s in chat["guards"])

    retr = client.post(
        "/api/chat", json={"user_id": "demo_trace", "message": "今天天气怎么样"}
    ).json()["agent_trace"]
    assert retr["retrieval_used"] is True

    sensor = client.post(
        "/api/sensors/apply-preset",
        json={"user_id": "demo_trace", "preset_id": "poor_sleep"},
    ).json()["agent_trace"]
    assert sensor["state_event"]["kind"] == "state_event"
    assert any(s["kind"] == "tool" for s in sensor["tools"])
