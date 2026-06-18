# Backend — Elderly Companion AI

FastAPI + Pydantic v2 backend. Slice 1 implements the minimal text-chat loop:
a health check and `POST /api/chat` answered by a fake LLM provider, returning
`response_text` plus a baseline `agent_trace`. It runs fully offline in
`DEMO_MODE=true`.

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

## API (Slice 1)

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
    "agents": [{ "kind": "agent", "name": "CompanionAgent", "summary": "..." }],
    "tools": [],
    "guards": [],
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

## Layout

```text
app/
  main.py                  FastAPI app factory + CORS
  core/config.py           Settings (env / .env), DEMO_MODE, providers
  core/constants.py        Enums: CompanionMode / RiskLevel / Route / TraceEntryKind
  api/routes/health.py     GET  /api/health
  api/routes/chat.py       POST /api/chat
  schemas/chat.py          ChatRequest / ChatResponse
  schemas/trace.py         AgentTrace / TraceStep
  services/llm_provider.py LLMProvider interface + get_llm_provider()
  services/fake_llm_provider.py  Offline deterministic fake provider
tests/                     health / chat / trace schema / provider fallback
```

## Not in Slice 1

CoordinatorAgent routing (#5), InputRuleGuard / OutputRuleGuard /
SafetyCriticAgent (#8), real CompanionAgent persona (#6), trace persistence and
Trace Panel API (#9), memory / reminders / sensors / retrieval / voice. The
`agent_trace` schema is already shaped so those slot in without breaking it.
