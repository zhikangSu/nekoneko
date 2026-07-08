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
  -d '{"user_id":"demo_user","message":"今天下午适合出去散步吗？","mode":"role_first","role_selection_mode":"auto"}'
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
  "role_selection_mode": "auto",
  "selected_role_ids": [],
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

`role_selection_mode` is `auto` or `manual` for relationship cueing turns.
`auto` keeps the default topic-based role orchestration. In `manual` mode,
`selected_role_ids` can contain up to three visible relationship roles such as
`same_age_peer`, `curious_junior`, or `theme_companion`; `no_ai_role` is
exclusive and suppresses staged role cueing. Sensitive topics still stay on the
boundary-safe route instead of producing role banter.

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
in `services/voice_provider`. In DEMO_MODE the mocks are deterministic and
offline: `MockASRProvider` returns a **simulated** transcript (no audio
decoding), `MockTTSProvider` synthesizes a short soft sine-tone WAV with the
stdlib `wave` module — a placeholder voice, but real playable/replayable audio.

**Real provider (#23, `XiaomiMiMo*VoiceProvider`).** Selection mirrors the LLM
provider: mock by name, **mock whenever `DEMO_MODE=true`** (so the demo never
needs a key), and the real xiaomimimo provider only when `DEMO_MODE=false` +
`ASR_PROVIDER`/`TTS_PROVIDER=xiaomimimo` + `OPENAI_API_KEY` is set; otherwise an
error. xiaomimimo serves voice through `/chat/completions` (omni-style), not
`/audio/*`: TTS puts the text in an *assistant* message with an `audio.voice`
preset and returns base64 WAV; ASR sends the clip as an `input_audio` **data URL**
(WAV/MP3) and returns the transcript as the message content. The provider retries
once on 429/5xx; a live failure is caught in the route and surfaces as
`ok=false` (ASR) or a `502` (TTS), so the chat degrades to text instead of
erroring. The key is read from the gitignored `.env` and never logged; tests
force the mock and never call the live API.

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
  services/              llm_provider · fake_llm_provider · xiaomimimo_llm_provider · voice_provider · mock_voice_provider · xiaomimimo_voice_provider
  prompts/               companion_role_first.md · companion_neutral_assistant.md
tests/                     guards · routing · safety · trace · memory · reminder · sensor · guardian · ...
```

Memory is markdown-first: each user's `memory.md` is the human-readable source of
truth, with a `memories.json` index for CRUD (under `MEMORY_ROOT/users/{id}/`).

## Real providers (opt-in)

A real **LLM** (companion replies) and real **ASR/TTS** (voice) are wired behind
the same provider interfaces, selected only with `DEMO_MODE=false` + the named
provider + `OPENAI_API_KEY`; `DEMO_MODE=true` always uses the fake/mock providers
(no key, deterministic). The real provider is xiaomimimo (OpenAI-compatible,
through `/chat/completions`):

- `LLM_PROVIDER=xiaomimimo` → `XiaomiMiMoLLMProvider` drafts the companion reply
  from the persona `system_prompt` `CompanionAgent` renders (model `mimo-v2-flash`
  by default). On any API failure it falls back to the fake reply, so a turn
  never breaks; the reply still passes `OutputRuleGuard` either way.
- `ASR_PROVIDER` / `TTS_PROVIDER=xiaomimimo` → real speech (see Voice I/O above).

Keys live only in the gitignored `.env` and are never logged; tests force the
fake/mock providers and never call the live API.

Real **retrieval** is available too: `RETRIEVAL_PROVIDER=open_meteo` (with
`DEMO_MODE=false`) fetches real weather / air quality from Open-Meteo — free, no
API key — for the configured location (`RETRIEVAL_LAT/LON/LOCATION`, default Hong
Kong); it falls back to the offline mock on any failure, and `DEMO_MODE=true`
always uses the mock. So with `DEMO_MODE=false` the LLM, voice, and retrieval can
all run on real providers.

## Not yet (later slices)

Stores persist as JSON + markdown; SQLite is the planned structured upgrade. Real
wearable APIs would only replace the `SensorAdapter` input — the `StateEvent`
contract stays.
