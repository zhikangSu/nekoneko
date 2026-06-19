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
`emergency_mock`; a present `state_event` → `proactive_checkin` (Guardian path,
dormant until #12/#22); otherwise → `companion_chat`. `SafetyCriticAgent` runs
**only** on flagged risk and returns a safe template (no diagnosis, no dosage, no
real emergency action). Every turn's trace is persisted under
`TRACE_LOG_DIR` and readable via `/api/traces`.

## Layout

```text
app/
  main.py                  FastAPI app factory + CORS
  core/config.py           Settings (env / .env), DEMO_MODE, providers, dirs
  core/constants.py        Enums: CompanionMode / RiskLevel / Route / TraceEntryKind
  api/routes/            health · chat · users · traces
  api/deps.py              get_profile_store / get_trace_store
  agents/                coordinator · companion · safety_critic
  tools/                 input_rule_guard · output_rule_guard
  safety/                risk_keywords · risk_classifier · templates/*.md
  graph/                 state · nodes · edges · build_graph (run_turn)
  schemas/               chat · trace · profile
  stores/                profile_store · trace_store
  services/              llm_provider · fake_llm_provider
  prompts/               companion_role_first.md · companion_neutral_assistant.md
tests/                     guards · coordinator routing · safety · trace store/API · ...
```

## Not yet (later slices)

GuardianAgent consuming StateEvent (#12/#22), MemoryTool / Memory Center (#10),
ReminderTool (#11), controlled retrieval (#13), real ASR/TTS (#4/#23). The
Coordinator's reminder / memory / retrieval routes and the `graph/` boundary are
shaped so those slot in. Real LLM provider wiring uses the `system_prompt` the
CompanionAgent already renders.
