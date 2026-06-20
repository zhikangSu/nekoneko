# Backend — Elderly Companion AI

FastAPI + Pydantic v2 backend. `POST /api/chat` runs a small agent graph and
returns `response_text` plus a persisted `agent_trace`:

```text
input guard → coordinator → (companion | safety | proactive) → output guard
```

Plus user-profile endpoints (#21) and trace-history endpoints (#9). Runs fully
offline in `DEMO_MODE=true` with the fake LLM provider.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optionally copy the env file (defaults already keep everything offline):

```bash
cp ../.env.example ../.env   # DEMO_MODE=true, LLM_PROVIDER=fake
```

## Run

```bash
uvicorn app.main:app --reload      # http://localhost:8000
```

- Health: `GET /api/health`
- Chat: `POST /api/chat`
- Profile: `GET|PATCH /api/users/{user_id}/profile`
- Traces: `GET /api/traces/{turn_id}`, `GET /api/traces?user_id=&limit=`
- Memory: `GET|POST /api/memory/{user_id}`, `DELETE /api/memory/{user_id}/{memory_id}`, `PATCH /api/memory/{user_id}/settings`
- Reminders: `GET|POST /api/reminders/{user_id}`, `DELETE /…/{id}`, `POST /…/{id}/confirm`, `POST /…/{id}/trigger`
- Sensors: `GET /api/sensors/presets`, `POST /api/sensors/apply-preset`, `POST /api/sensors/refuse`
- Voice: `POST /api/voice/asr` (raw audio body → transcript), `POST /api/voice/tts` (`{text}` → base64 audio)

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo_user","message":"今天下午适合出去散步吗？","mode":"role_first"}'
```

Interactive API docs: `http://localhost:8000/docs`.

## Test

```bash
pytest
```

Tests force `LLM_PROVIDER=fake` and never call real LLM / ASR / TTS / web APIs.

## API

`POST /api/chat`

Request:

```json
{
  "user_id": "demo_user",
  "message": "今天下午适合出去散步吗？",
  "mode": "role_first",
  "voice_enabled": false,
  "sensor_preset_id": null,
  "companion_display_name": null
}
```

Response:

```json
{
  "turn_id": "t_ab12cd34",
  "response_text": "...",
  "audio_url": null,
  "agent_trace": {
    "turn_id": "t_ab12cd34",
    "mode": "role_first",
    "route": "companion_chat",
    "risk_level": "low",
    "agents": [
      { "kind": "agent", "name": "CoordinatorAgent", "summary": "route = companion_chat：..." },
      { "kind": "agent", "name": "CompanionAgent", "summary": "..." }
    ],
    "tools": [],
    "guards": [
      { "kind": "guard", "name": "InputRuleGuard", "summary": "未发现高风险关键词" },
      { "kind": "guard", "name": "OutputRuleGuard", "summary": "输出无违规" }
    ],
    "state_event": null,
    "memory_used": false,
    "retrieval_used": false,
    "safety_critic_used": false
  }
}
```

`mode` is `role_first` or `neutral_assistant`. When `companion_display_name` is
unset, the backend uses the neutral fallback **陪伴 AI** — no fixed name is
hardcoded.

### Routing & safety

`CoordinatorAgent` picks one route per turn from `InputRuleGuard`'s risk level:
high-risk health/medication → `safety_response`; crisis (fall / help) →
`emergency_mock`; a reminder request → `reminder_management`; a time-sensitive
external-fact question (weather / air quality) → `retrieval_supported_response`;
a present `state_event` → `proactive_checkin`; otherwise → `companion_chat`.
`SafetyCriticAgent` runs **only** on flagged risk
and returns a safe template (no diagnosis, no dosage, no real emergency action).
Every turn's trace is persisted under `TRACE_LOG_DIR` and readable via
`/api/traces`.

On the companion path, `MemoryTool` reads long-term memory before the reply
(`memory_used`) and extracts new preferences after it (skipped while the user has
paused extraction). The `reminder_management` route parses a phrase like
「每天早上8点提醒我吃药」into a reminder and restates it; medication reminders say
only "按医嘱" — dosage questions are caught earlier and routed to safety.

The `retrieval_supported_response` route runs `InfoRetrievalTool` (mock weather /
air quality in DEMO_MODE) **before** the companion reply, so the companion
rewrites the external fact warmly with memory. "Default no web" means no web
search / browser call unless the turn needs a time-sensitive external fact — it
does **not** mean "no LLM". Emotional / reminiscence turns never retrieve; dosage
questions go to safety, never search for a dose. The trace shows whether
retrieval happened and the mock source.

### Proactive care (sensors → StateEvent → Guardian)

`POST /api/sensors/apply-preset` makes the boundary explicit: `SensorAdapter`
encodes a mock `RawSignal` into a structured `StateEvent`, and `GuardianAgent`
decides on the StateEvent (never raw values) — `check_in` / `defer` /
`silent_log` / `safety_escalation`. Restraint comes from cross-turn welfare_state:
same-type cooldown, a daily cap, quiet hours, and a 24h refusal pause
(`/api/sensors/refuse`). The mock physiological anomaly is low-confidence with
`medical_claim_allowed=false`, so Guardian makes no medical claim. Each decision
is persisted as a trace (SensorAdapter tool + StateEvent + GuardianAgent agent).

### Voice I/O (mock pipeline, #4)

`POST /api/voice/asr` takes the recorded clip as the **raw request body** (no
multipart dependency) and returns a transcript; `ok=false` means nothing was
recognized, so the UI shows a gentle retry prompt and the text path still works.
`POST /api/voice/tts` takes reply text and returns base64 audio, cached per text
so replay is free (`cached=true`). Both sit behind `ASRProvider` / `TTSProvider`
in `services/voice_provider`, selected like the LLM provider (mock by name, mock
fallback in DEMO_MODE, otherwise an error). In DEMO_MODE the mocks are
deterministic and offline: `MockASRProvider` returns a **simulated** transcript
(no audio decoding), `MockTTSProvider` synthesizes a short soft sine-tone WAV
with the stdlib `wave` module — a placeholder voice, but real playable/replayable
audio. A real ASR/TTS provider arrives with #23 behind the same interface.

## Layout

```text
app/
  main.py                  FastAPI app factory + CORS
  core/config.py           Settings (env / .env), DEMO_MODE, providers, dirs
  core/constants.py        Enums: CompanionMode / RiskLevel / Route / TraceEntryKind
  api/routes/            health · chat · users · traces · memory · reminders · sensors · voice
  api/deps.py              get_*_store (profile / trace / memory / reminder / guardian)
  agents/                coordinator · companion · safety_critic · guardian
  tools/                 input/output_rule_guard · memory_tool · reminder_tool · info_retrieval · sensor_adapter · sensor_simulator
  safety/                risk_keywords · risk_classifier · templates/*.md
  graph/                 state · nodes · edges · build_graph (run_turn)
  schemas/               chat · trace · profile · memory · reminder · sensor · voice
  stores/                profile · trace · memory · reminder · guardian_state
  services/              llm_provider · fake_llm_provider · voice_provider · mock_voice_provider
  prompts/               companion_role_first.md · companion_neutral_assistant.md
tests/                     guards · routing · safety · trace · memory · reminder · sensor · guardian · ...
```

Memory is markdown-first: each user's `memory.md` is the human-readable source of
truth, with a `memories.json` index for CRUD (under `MEMORY_ROOT/users/{id}/`).

## Not yet (later slices)

A real ASR/TTS provider (#23) and a real LLM/retrieval provider — the
`ASRProvider` / `TTSProvider` / `LLMProvider` interfaces and the `graph/`
boundary are shaped so those slot in (the voice mock→real seam mirrors
`InfoRetrievalTool`). Stores persist as JSON + markdown; SQLite is the planned
structured upgrade. Real wearable APIs would only replace the `SensorAdapter`
input — the `StateEvent` contract stays.
