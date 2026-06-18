# User-Named Elderly AI Companion

> **愿意回来，放心使用。陪伴优先，必要时查询，安全始终在线。**
> **Return willingly, use safely. Companionship first, retrieval when needed, safety always.**

A **relationship-first voice companion AI prototype for older adults** that helps
users feel heard, remembered, safe, and in control. Built for **CityU MSDS
SDSC6002 Research Project, Summer 2026** as a course-level software demo and HCI
research prototype.

This is **not** a generic assistant, a search engine, a medical chatbot, or an
addictive companion product. It does **not** perform medical diagnosis, dosage
advice, or real emergency dispatch.

The companion has **no built-in fixed name**. The user names it during
onboarding; before naming, the UI shows the neutral label **陪伴 AI / AI
Companion** and the code stores the user's choice in `companion_display_name`.

---

## Documentation map

Read the canonical documents in this order. Start with `00` for orientation.

| Doc | Purpose |
|---|---|
| [docs/00_overview](docs/00_overview_elderly_companion_ai.md) | One-page index, positioning, reading order. |
| [docs/01_prd](docs/01_prd_elderly_multi_agent_companion_ai.md) | Product requirements, MVP, priorities, evaluation. |
| [docs/02_technical_roadmap](docs/02_technical_roadmap_elderly_multi_agent_companion_ai.md) | Architecture, agent/tool split, API, roadmap, demo script. |
| [docs/03_fxy_integration_review](docs/03_fxy_integration_review.md) | Record of absorbing / downgrading / rejecting a teammate draft. |
| [docs/04_engagement_agent_optimization_review](docs/04_engagement_agent_optimization_review.md) | Role-first, well-being-first, real-agent optimization record. |
| [docs/05_reference_project_structure](docs/05_reference_project_structure.md) | Repo layout reference for initialization and development. |
| [docs/06_collaboration_workflow](docs/06_collaboration_workflow.md) | AI-first, mainline-first collaboration and PR workflow. |

Working docs produced for the demo:

| Doc | Purpose |
|---|---|
| [docs/demo_script.md](docs/demo_script.md) | The 6 final-demo scenarios, step by step. |
| [docs/safety_policy.md](docs/safety_policy.md) | What the system must never do, and the high-risk safety path. |
| [docs/evaluation_plan.md](docs/evaluation_plan.md) | HCI evaluation goals, measures, and study conditions (draft). |

Contributor instructions for AI coding agents: [AGENTS.md](AGENTS.md) (global
product/safety/architecture rules) and [CLAUDE.md](CLAUDE.md) (Claude Code
workflow). Design-decision records live in [docs/adr/](docs/adr/).

---

## Architecture at a glance

```text
User voice/text
→ Voice I/O service (if voice)
→ InputRuleGuard
→ CoordinatorAgent
   ├── CompanionAgent
   ├── GuardianAgent
   ├── SafetyCriticAgent (only on detected risk / uncertainty)
   └── tools / services
→ OutputRuleGuard
→ TTS (if voice)
→ AgentTracePanel
```

Only these are **autonomous agents**: `CoordinatorAgent`, `CompanionAgent`,
`GuardianAgent`, `SafetyCriticAgent`. Everything else
(`MemoryTool`, `ReminderTool`, `InfoRetrievalTool`, `SensorAdapter`,
`InputRuleGuard`/`OutputRuleGuard`, `ASRService`/`TTSService`, `LLMProvider`, …)
is a **tool** or **service**. The Agent Trace must keep this distinction visible.

---

## Repository layout

```text
.
├── docs/        Canonical product/technical docs (00–06) + working docs
├── backend/     FastAPI + Pydantic v2 backend (agents, tools, services, API)
├── frontend/    Next.js + TypeScript + Tailwind web UI
├── data/        Local demo data: SQLite, markdown memory, traces, audio cache
├── scripts/     Seed / reset / export / demo-runner scripts
├── AGENTS.md    Global rules for AI coding agents
└── CLAUDE.md    Claude Code workflow expectations
```

See [docs/05_reference_project_structure.md](docs/05_reference_project_structure.md)
for the full intended structure.

---

## Quick start (DEMO_MODE)

The demo runs fully offline with fake/mock providers — no paid API keys.

```bash
cp .env.example .env          # keep DEMO_MODE=true and fake/mock providers
```

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload   # serves http://localhost:8000
pytest                          # runs offline with the fake provider
```

Health check: `GET http://localhost:8000/api/health`.
Try one chat turn:

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo_user","message":"今天下午适合出去散步吗？","mode":"role_first"}'
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev                     # serves http://localhost:3000
```

Open `http://localhost:3000`, send a text message, and watch the placeholder
trace appear. Set `NEXT_PUBLIC_API_BASE_URL` in `.env` if the backend is not on
`http://localhost:8000`.

> Commands above are the target developer experience for Slice 1. Each backend /
> frontend folder also has its own README with the exact, current commands.

---

## Demo route

The final demo follows six scenarios (full script in
[docs/demo_script.md](docs/demo_script.md)):

1. **Companionship** — emotional disclosure gets emotional grounding first.
2. **Reminder** — set a medication/hydration/schedule reminder (no dosage advice).
3. **Memory** — the system remembers a stated preference and reuses it; the user
   can view and delete it.
4. **Proactive care** — a mock "Poor Sleep" sensor preset triggers a gentle,
   restrained check-in.
5. **Controlled retrieval** — a weather/time-sensitive question triggers
   retrieval; emotional turns do not.
6. **Safety boundary** — a medication-dosage / high-risk health question is
   refused with a safe alternative, never diagnosed.

---

## Safety boundaries (must always hold)

The system must never provide medical diagnosis, medication dosage changes,
treatment recommendations, claims that mock sensor data proves illness, real
emergency dispatch, or fabricated family/hospital/caregiver information. High-risk
input is routed to the safety path. See [docs/safety_policy.md](docs/safety_policy.md)
and [AGENTS.md](AGENTS.md) §4, §9, §12.

---

## Contributing

This repo is optimized for AI-first development with asynchronous review. One
main completer advances P0 vertical slices; a reviewer checks PR behavior and
safety in daily batches. Read
[docs/06_collaboration_workflow.md](docs/06_collaboration_workflow.md) before
opening a PR, and use [.github/pull_request_template.md](.github/pull_request_template.md).
Keep `DEMO_MODE=true` runnable and never hardcode a fixed companion name.
