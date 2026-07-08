# AGENTS.md

Project: **A Multi-Agent Collaborative Companion Robot for Older Adults**  
Working name: **User-Named Elderly AI Companion**  
Course: **CityU MSDS SDSC6002 Research Project, Summer 2026**  
Current stage: **course-level software demo / HCI research prototype**

This file gives global instructions for AI coding agents such as Codex, Claude Code, Cursor agents, or other automated contributors working in this repository.

---

## 1. Read this first

Before making code changes, read the canonical project documents in this order:

```text
docs/00_overview_elderly_companion_ai.md
docs/01_prd_elderly_multi_agent_companion_ai.md
docs/02_technical_roadmap_elderly_multi_agent_companion_ai.md
docs/03_fxy_integration_review.md
docs/04_engagement_agent_optimization_review.md
docs/05_reference_project_structure.md
docs/06_collaboration_workflow.md
```

Also follow:

```text
.github/pull_request_template.md
```

Core slogan:

> **愿意回来，放心使用。陪伴优先，必要时查询，安全始终在线。**  
> **Return willingly, use safely. Companionship first, retrieval when needed, safety always.**

---

## 2. Product north star

The goal is not to build a generic assistant, a search engine, a medical chatbot, or an addictive companion product.

The goal is to build a **relationship-first voice companion AI prototype for older adults** that helps users feel heard, remembered, safe, and in control.

The target audience is the broad older adult population. Do not narrow behavior, UI, or testing assumptions to a single subgroup such as only isolated, frail, or high-risk users.

The MVP evaluates **interaction feasibility, trust, perceived companionship, willingness to continue use, and perceived appropriateness of proactive care**. It does **not** evaluate clinical effectiveness.

---

## 3. Current collaboration model

Use `docs/06_collaboration_workflow.md` as the execution guide.

Current practical model:

```text
one main completer advances P0 vertical slices
reviewer checks PR behavior and safety asynchronously, usually in daily batches
other contributors may add non-blocking docs / QA / test cases if and when available
```

Do not assume traditional four-person parallel ownership. Issues are an ordered task queue, not a strict personal assignment table.

### 3.1 Mainline execution order

Follow P0 vertical slices in this order unless the user explicitly changes priority:

```text
Slice 1: #1 docs entry → #2 frontend shell → #3 FastAPI chat baseline
Slice 2: #21 first-run onboarding → #6 CompanionAgent persona
Slice 3: #5 Coordinator → #8 Safety → #9 Agent Trace
Slice 4: #10 Memory → #11 Reminder
Slice 5: #22 SensorAdapter / StateEvent → #12 GuardianAgent
Slice 6: #13 controlled retrieval
Slice 7: #4 mock voice UI → #23 real ASR/TTS provider
Slice 8: #14 tests → #16 final demo materials
```

Do not start P1 issues until the relevant P0 slice is stable.

### 3.2 PR workflow

Make non-trivial changes on branches and open PRs using `.github/pull_request_template.md`.

A main completer may open several small PRs before reviewer feedback arrives, as long as:

```text
- each PR is issue-scoped or slice-scoped;
- PR dependencies are clearly stated;
- unrelated files are not refactored;
- DEMO_MODE=true remains runnable;
- no fixed companion name, medical advice, or real emergency action is introduced.
```

At the end of every AI coding session, leave a handoff in the PR or issue:

```md
Completed:
- ...

Tested:
- ...

Not done:
- ...

Risks / questions:
- ...

Next recommended step:
- ...
```

### 3.3 User feedback issue-to-PR workflow

When the user reports a concrete problem, bug, confusing behavior, or product
gap, do not jump straight into broad changes. Use this workflow by default:

```text
1. Reproduce or inspect the reported behavior locally.
2. Confirm whether it is a real issue, a configuration problem, expected mock behavior, or a documentation mismatch.
3. Create or update a GitHub issue that records:
   - the user's reported symptom;
   - reproduction steps or screenshots/logs;
   - the confirmed root cause or current hypothesis;
   - the intended acceptance criteria.
4. Create a focused branch for the issue.
5. Make the smallest targeted fix that addresses the confirmed problem.
6. Run the relevant backend/frontend tests or explain any test gap.
7. Open a PR linked to the issue, using `.github/pull_request_template.md`.
8. Review the PR scope and behavior against the issue acceptance criteria.
9. Merge the PR back into `main` after it is ready.
10. Pull or verify `main`, then report the outcome and any remaining follow-up.
```

Do not let user feedback disappear into chat history. If it changes the project
backlog, implementation, or demo behavior, it should be represented by an issue
and resolved through a PR.

---

## 4. Non-negotiable design principles

### 4.1 Role-first, not assistant-first

The user-facing companion persona must be **user-named, not hardcoded**.

Use `companion_display_name` as a configurable user setting chosen by the user during onboarding or settings.

If the user has not named the companion yet, use neutral labels such as:

```text
陪伴 AI / AI Companion
```

Do not invent or hardcode a fixed default name in prompts, UI copy, seed data, tests, snapshots, or demo scripts.

The relationship feel should be like a familiar community junior, kind neighbor, or patient old friend. It can feel warm and human-like, but must never pretend to be a real person, doctor, family member, or caregiver.

### 4.2 Optimize for well-being, not stickiness

Do not optimize for addiction, dependency, endless engagement, or emotional lock-in.

The system must:

```text
allow users to stop, pause, reject, or disable proactive check-ins
encourage real-world support from family, friends, doctors, community services, or caregivers when appropriate
avoid language like “only I understand you” or “you do not need other people”
avoid over-personalized emotional manipulation
```

### 4.3 Companionship first, retrieval when needed

Do not call external realtime retrieval for emotional disclosure, reminiscence, routine chit-chat, memory management, or simple reminders.

Call retrieval only for time-sensitive or external facts such as:

```text
today / now / latest / recent / nearby / weather / air quality / community service / opening hours / factual verification
```

Here, “default not online” means **do not call web search / browser / external retrieval tools**. It does **not** mean the app cannot call a hosted LLM API.

### 4.4 Safety always

The system must never provide:

```text
medical diagnosis
medication dosage changes
treatment recommendations
claims that mock sensor data proves illness
real emergency service dispatch
fabricated family, hospital, or caregiver information
overconfident mental health crisis handling
```

High-risk content must trigger the safety path.

---

## 5. Agent vs tool distinction

Do not call every module an agent. In reports, code, and trace UI, use this distinction.

### 5.1 Autonomous agents

A module may be called an **Agent** only if it has a goal, cross-turn state or policy, contextual decision-making power, and explainable decisions.

MVP autonomous agents:

```text
CoordinatorAgent
CompanionAgent
GuardianAgent
SafetyCriticAgent
```

### 5.2 Tools and services

These are tools/services, not autonomous agents:

```text
EmotionClassifierTool
MemoryTool / MemoryStore
ReminderTool / ReminderScheduler
InfoRetrievalTool
SensorSimulatorTool
SensorAdapter / StateEncoder
InputRuleGuard / OutputRuleGuard
VoiceIOService
ASRService
TTSService
LLMProvider
```

Agent Trace must clearly distinguish:

```text
Agent / Tool / Guard / StateEvent / Retrieval / Memory
```

---

## 6. MVP scope

P0 first:

```text
1. Text chat core before voice.
2. First-run onboarding and user-named companion persona.
3. Coordinator + Companion + Guardian + SafetyCritic skeleton.
4. Agent trace for every chat turn.
5. Memory Center: view / add / delete / pause memory.
6. Reminder CRUD: medication, hydration, schedule reminders.
7. SensorAdapter + Sensor Simulator + Guardian proactive check-ins.
8. Controlled retrieval: weather / time-sensitive factual query only.
9. Input/output rule guards and high-risk safety templates.
10. Voice I/O: mock first, real ASR/TTS provider after text pipeline is stable.
```

P1 only after P0 is stable:

```text
VAD / interruption detection
TTS interruption
feedback words such as “嗯 / 对”
reminiscence topic mode
caregiver mock dashboard
evaluation data export
trace-visible vs trace-hidden study condition
more proactive personalization
```

Future work / do not implement unless explicitly requested:

```text
real Apple Watch / HealthKit integration
real hospital integration
real emergency calling
fall detection
clinical diagnosis
medication database or drug interaction advice
longitudinal clinical study
real 65+ participant study without ethics/supervisor approval
local LLM as primary runtime
full-duplex realtime voice
```

---

## 7. Recommended technical stack

Use this unless a task explicitly changes it:

```text
Frontend: Next.js + TypeScript + React + TailwindCSS
Backend: Python 3.11+ + FastAPI + Pydantic v2
Agent orchestration: LangGraph or a compatible graph/state-machine abstraction
Database: SQLite for MVP, Postgres optional later
Memory: markdown-first source of truth + SQLite structured data + optional vector index
Scheduler: APScheduler or simple event loop
Runtime LLM: configurable provider, fake provider by default in tests
ASR/TTS: mock provider first, API provider later
Deployment: local demo first, cloud optional
```

Keep external providers behind interfaces so the demo can run in `DEMO_MODE=true` without paid APIs.

---

## 8. Environment and secrets

Never hardcode secrets. Never commit real API keys.

Use `.env` locally and keep `.env.example` committed.

Recommended environment variables:

```bash
DEMO_MODE=true
APP_ENV=development

LLM_PROVIDER=fake          # fake | openai | anthropic | local
ASR_PROVIDER=mock          # mock | openai | browser
TTS_PROVIDER=mock          # mock | openai | edge
RETRIEVAL_PROVIDER=mock    # mock | weather_api | openai_web_search
LLM_MODEL=mimo-v2.5        # when using xiaomimimo; v2 / v2-flash are unsupported

OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WEATHER_API_KEY=

DATABASE_URL=sqlite:///./data/app.db
MEMORY_ROOT=./data/memory
TRACE_LOG_DIR=./data/traces
MAX_LLM_CALLS_PER_TURN=2
MAX_WEB_CALLS_PER_TURN=1
```

Tests must not call real LLM, ASR, TTS, or web APIs.

---

## 9. Safety architecture

Safety must not be a single final prompt slapped on every answer.

Use this structure:

```text
InputRuleGuard
  → risk classification
  → Coordinator route
  → Companion draft or safe template
  → OutputRuleGuard
  → SafetyCriticAgent only if risk is detected or uncertainty is high
  → final response
```

High-risk triggers include but are not limited to:

```text
胸痛 / 呼吸困难 / 晕倒 / 摔倒 / 意识不清 / 严重头晕
自杀 / 想死 / 不想活 / 伤害自己
药吃多了 / 忘记吃药要不要补 / 能不能吃两片 / 换药 / 加药 / 停药
救命 / 帮帮我 / 联系急救
```

Do not implement real phone calls, SMS, hospital dispatch, caregiver notification, or emergency automation. Implement mock emergency UI only.

---

## 10. Memory and privacy rules

Use transparent, user-controllable memory.

Memory Center should support:

```text
view
edit if applicable
delete
pause / disable categories
```

Memory layers:

```text
Short-term state: current LangGraph thread / chat session
Markdown memory: human-readable source of truth
SQLite memory: structured profile, consent, reminders, audit metadata
Vector memory: optional derived index from approved summaries
```

Do not automatically save:

```text
passwords
ID numbers
financial information
sensitive health details
unverified emotional inference
family conflict
temporary negative mood
anything the user asks the system to forget
```

Whenever uncertain, ask for confirmation or do not save.

`companion_display_name` belongs to UserProfile / onboarding, not ordinary event memory.

---

## 11. Guardian and proactive care rules

GuardianAgent is responsible for proactive but restrained check-ins.

Important boundary:

```text
raw/mock signal → SensorAdapter / StateEncoder → StateEvent → GuardianAgent decision
```

GuardianAgent must not directly interpret raw sensor values or make medical claims from sensor presets.

Required Guardian output should include:

```json
{
  "care_proposal": "...",
  "restraint_critique": "...",
  "decision": "check_in | defer | silent_log | safety_escalation",
  "reason": "...",
  "cooldown_applied": true,
  "trace_visible_summary": "..."
}
```

Default constraints:

```text
same-topic check-in cooldown: 2 hours
daily proactive casual check-ins: max 3
quiet hours: 22:00–07:00 by default
user refusal: pause same topic for 24 hours
night voice output: off by default unless explicitly enabled
```

Use soft, uncertain wording such as:

```text
看起来可能比平时少一点
如果现在方便，我可以陪您聊两句
```

Avoid:

```text
您今天身体不好
您可能生病了
您一定很孤独
```

---

## 12. Controlled retrieval rules

InfoRetrievalTool may be called only when the Coordinator has a reason.

Allowed retrieval examples:

```text
今天下午适合散步吗？ → weather / air quality
附近社区中心今天开门吗？ → public service lookup
最近有没有什么诈骗新闻？ → current news / safety information
帮我确认这个通知是真的吗？ → factual verification, if safe
```

Do not retrieve for:

```text
我今天想老伴了
我有点孤独
你还记得我喜欢什么吗
帮我每天八点提醒吃药
忘记我喜欢粤剧这件事
```

Medication dosage questions must not search for dosage answers. Route to safety.

---

## 13. Agent trace requirements

Every `/api/chat` response must include an `agent_trace` object, even in demo mode.

Trace should include:

```text
turn_id
mode
route
risk_level
agents
tools
guards
state_event if any
memory_used
retrieval_used
safety_critic_used
```

The trace is both a product feature and a research artifact. Keep it stable.

---

## 14. Coding guidelines

General:

```text
work issue by issue
prefer small, reviewable diffs
avoid broad refactors
keep P0 simple and stable before P1
add type hints and validation at API boundaries
do not run real paid API calls in tests
```

Backend:

```text
agents under backend/app/agents/
tools under backend/app/tools/
external wrappers under backend/app/services/
graph construction under backend/app/graph/
prompts under backend/app/prompts/
safety templates under backend/app/safety/templates/
```

Frontend:

```text
large buttons
accessible typography
clear voice controls
transcript fallback
Memory Center with delete/pause controls
Agent Trace Panel in demo mode
no youth slang, memes, or overly playful copy
```

Prompts should be versioned as files, not buried inside code.

---

## 15. Definition of done

A feature is done only when:

```text
it satisfies the PRD acceptance criteria
it works in DEMO_MODE=true without external paid API calls
it has relevant unit or integration tests, or explains why tests are not available yet
it produces trace entries if it affects chat behavior
it respects safety, memory, naming, retrieval, and proactive care rules
it has no hardcoded secrets
it does not expand scope into P1/Future without explicit approval
it is documented if it changes public API, prompts, or data models
```

---

## 16. Do not do these things

Do not:

```text
turn the user-named companion persona into a generic assistant
hardcode a fixed companion name
remove safety boundaries
call tools agents in trace or docs
make every response call web search
make every response call SafetyCritic LLM
silently save private or sensitive memories
implement real emergency calling
claim the system detects illness, depression, loneliness, or falls
add large unrequested features
overwrite canonical docs or backups unless asked
commit .env, API keys, raw participant data, or real recordings
```
