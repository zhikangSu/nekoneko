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

> **Scope honesty.** The code in this repo is a **course-level software demo / HCI
> research prototype**, not a finished clinical or care product. No elderly user
> study has been run yet. `DEMO_MODE` defaults to fake/mock/offline providers with
> no API key; optional xiaomimimo LLM/ASR/TTS and Open-Meteo weather providers are
> available behind interfaces. Long-term memory, trust, and control are
> **supporting / boundary / evaluation dimensions**, not a standalone contribution.

---

## Documentation

This repository is a demo-focused snapshot: it contains everything needed to run
and evaluate the prototype. The full product, research, and process documentation
set (PRD, technical roadmap, evaluation plan, study materials, contributor
guides) is maintained in the team's development repository.

For a complete feature checklist and step-by-step acceptance scenarios, see the
[QAQ Feature Experience and Test Guide](FEATURE_TEST_GUIDE.md)（中文）.

Poster and coursework handoff materials:

- [Current project status and poster refinement brief](docs/07_project_status_for_poster.md)（中文）
- [5–8 minute bilingual poster presentation script](docs/08_poster_presentation_script_bilingual.md)
- [English SDSC6002 project report](docs/09_course_project_report.md)
- [Current A0 poster source and previews](output/poster/)

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
├── backend/     FastAPI + Pydantic v2 backend (agents, tools, services, API)
├── frontend/    Next.js + TypeScript + Tailwind web UI
├── data/        Local demo data: seed memory cards, traces, audio cache
├── docs/        Poster handoff, presentation script, report, and evidence images
├── output/      A0 poster source/previews and the functional test report
├── scripts/     Dev runner scripts
├── FEATURE_TEST_GUIDE.md  Chinese feature and acceptance-test guide
└── Makefile     make setup / make dev / make test
```

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

Open `http://localhost:3000`, send a text message, and inspect the per-turn
Agent Trace. Set `NEXT_PUBLIC_API_BASE_URL` in `.env` if the backend is not on
`http://localhost:8000`.

Each backend / frontend folder also has its own README with exact commands.

### Real LLM and voice (optional)

The demo defaults to fake replies and mock voice. To use real **xiaomimimo**
companion replies, ASR, and TTS (the key lives only in the gitignored `.env`),
set in the repo-root `.env`:

```bash
DEMO_MODE=false
LLM_PROVIDER=xiaomimimo
ASR_PROVIDER=xiaomimimo
TTS_PROVIDER=xiaomimimo
RETRIEVAL_PROVIDER=mock
OPENAI_API_KEY=your_key_here
LLM_MODEL=mimo-v2.5
```

Restart the backend, then record in the browser. Provider failures fall back to
safe fake/mock behavior. Keep `RETRIEVAL_PROVIDER=mock` for the acceptance guide's
`mock_weather` expectation, or set it to `open_meteo` for real weather retrieval.
The endpoint rate-limits bursts, so don't click rapidly.

---

## Demo route

The current prototype supports the following core scenarios. The full 12-feature
acceptance matrix and exact test prompts are in
[FEATURE_TEST_GUIDE.md](FEATURE_TEST_GUIDE.md).

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
7. **Relationship-aware reminiscence** — 2–3 relationship roles provide a short
   social cue before inviting the elder into a memory topic.
8. **Trace and caregiver summary** — inspect routing and privacy-preserving
   metadata without exposing complete transcripts. Research evaluation export
   remains implemented but is hidden from the coursework UI by default.

---

## Safety boundaries (must always hold)

The system must never provide medical diagnosis, medication dosage changes,
treatment recommendations, claims that mock sensor data proves illness, real
emergency dispatch, or fabricated family/hospital/caregiver information. High-risk
input is routed to the safety path: deterministic input/output rule guards run on
every turn, a SafetyCriticAgent reviews flagged turns, and high-risk cases fall
back to fixed safety templates that recommend contacting a doctor, family, or
emergency services (in demo mode the UI states that no real call is placed).

---

## Contributing

Active development happens in the team's development repository; this snapshot
tracks its main branch. For any change, keep `DEMO_MODE=true` runnable and never
hardcode a fixed companion name.
