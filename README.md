# Relationship-Aware Elderly Reminiscence Companion

> **让老人愿意开口回忆，自然地被"一群人"接住。**
> **Help older adults ease into reminiscence, gently received by a small group of AI relationship roles.**

A **relationship-aware reminiscence companion for older adults**. Instead of one
assistant answering questions, the system **dynamically orchestrates several AI
relationship roles** and lets them exchange a few short lines as a **social cue**,
so the elder is invited into memory and self-expression more naturally — and never
pushed. Built for **CityU MSDS SDSC6002 Research Project, Summer 2026** as an HCI
research prototype.

### Three core mechanisms (the research main line)

1. **关系编排 · Relationship orchestration** — based on the topic, the elder's life
   experience, emotional state, relationship preferences, and boundary needs, the
   system decides **who speaks, who stays silent, who follows up, who summarizes,
   and when to stop**.
2. **社会线索引入话题 · Social cueing** — 2–3 AI roles have a brief conversation
   around a photo / old object / life topic, forming a lightweight multi-person chat
   scene, and **then** invite the elder to join — a lower-pressure opener than asking
   the elder a question directly.
3. **多智能体角色交互 · Multi-agent role interaction** — different relationship roles
   (同龄共鸣 / 晚辈好奇 / 中年传承 / 回忆整理 / 边界守护) cooperate through rules of
   **共鸣 · 追问 · 总结 · 沉默 · 边界守护**, so the scene avoids noise (吵),
   inauthenticity (假), overload (乱), and boundary violations.

### Main research question

> 老年回忆陪伴中，系统如何基于话题、人生经历、关系偏好和边界需求，动态编排不同 AI
> 关系角色，并通过多智能体短对话作为社会线索，更自然地引导老人进入回忆与自我表达？

Sub-questions:

- **RQ1 关系编排** — 不同话题下哪些关系角色更适合出现？系统如何决定谁说话、谁沉默、谁总结、何时停止？
- **RQ2 社会线索引入话题** — agent–agent 的短对话线索是否比直接提问更自然、更低压力、更容易启动回忆？
- **RQ3 多智能体角色交互** — 同龄共鸣、晚辈好奇、中年传承、回忆整理、边界守护等角色如何协作，才能避免噪声和越界？

Boundaries (deceased / grief / privacy / dependency) are treated as an **ethics
discussion**, not a fourth research question: when a topic touches these, the system
**pauses, redirects, or gently declines** rather than pressing on. It never role-plays
a deceased person.

### Core contributions

- a **relationship-role taxonomy** for reminiscence companionship (关系角色分类);
- **dynamic relationship orchestration** driven by topic × experience × preference × boundary (动态关系编排);
- **agent–agent conversational cueing** as a social memory cue (社会线索引入话题);
- **role interaction rules**: 共鸣 / 追问 / 总结 / 沉默 / 边界守护;
- a **role / topic / boundary trace** that makes each orchestration decision inspectable.

### Supporting capabilities (technical foundation, not the contribution)

Reminders, weather / air-quality retrieval, mock sensor state, and voice I/O are
**supporting capabilities** on the technical foundation. They keep the companion
useful and the demo runnable, but they are **not** the research contribution and must
not be presented as such.

This is **not** a generic assistant, a search engine, a medical chatbot, or an
addictive companion product. It does **not** perform medical diagnosis, dosage
advice, or real emergency dispatch, and never role-plays a deceased person.

The companion has **no built-in fixed name**. The user names it during
onboarding; before naming, the UI shows the neutral label **陪伴 AI / AI
Companion** and the code stores the user's choice in `companion_display_name`.

> **Scope honesty.** The code in this repo is a **technical foundation / demo
> backbone**, not the finished research. The relationship-aware layer (dynamic role
> orchestration, agent–agent social cueing, and the relationship-role interaction
> rules) is the **next stage**, added as a relationship-aware prototype / Wizard-of-Oz
> / semi-automatic layer. No elderly user study has been run yet. **Real LLM and real
> retrieval are provider-interface / future work — not implemented**; `DEMO_MODE`
> defaults to fake/mock/offline providers with no API key. Real ASR/TTS is optional
> and available. Long-term memory, trust, and control are **supporting / boundary /
> evaluation dimensions**, not a standalone contribution.

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
| [docs/demo_script.md](docs/demo_script.md) | The 6 final-demo scenarios, step by step (with the Agent Trace for each). |
| [docs/demo_video_checklist.md](docs/demo_video_checklist.md) | Shot-by-shot checklist for recording the demo video. |
| [docs/poster_outline.md](docs/poster_outline.md) | Final research poster outline. |
| [docs/final_report_skeleton.md](docs/final_report_skeleton.md) | Fillable final-report structure. |
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

### One command (recommended)

```bash
make setup     # first time only — installs backend + frontend deps, creates .env
make dev       # backend (:8000) + frontend (:3000) together; Ctrl-C stops both
make test      # backend pytest + frontend build
```

Then open `http://localhost:3000` and name the companion. To run the two sides
separately (or without `make`), use the steps below.

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

Each backend / frontend folder also has its own README with exact commands.

### Real voice (optional)

The demo defaults to mock voice. To use the real **xiaomimimo** ASR/TTS (the key
lives only in the gitignored `.env`), set in the repo-root `.env`:

```bash
DEMO_MODE=false
ASR_PROVIDER=xiaomimimo
TTS_PROVIDER=xiaomimimo
# keep LLM_PROVIDER=fake and RETRIEVAL_PROVIDER=mock — a real LLM / retrieval
# provider is not implemented yet (companion replies stay template-based).
```

Restart the backend, then record in the browser. On any ASR/TTS failure the chat
degrades to text. The endpoint rate-limits bursts, so don't click rapidly.

---

## Demo route

The current demo backbone follows six scenarios (full script in
[docs/demo_script.md](docs/demo_script.md)). These exercise the **supporting
capabilities and safety path** on the technical foundation; the relationship-aware
reminiscence flow (dynamic role orchestration + agent–agent social cueing) is the
**next-stage** prototype layer that builds on top of them.

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
