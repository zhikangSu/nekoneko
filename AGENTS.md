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
```

Treat these files as product and research specifications. Do **not** rewrite them unless the task explicitly asks for documentation changes.

Core slogan:

> **愿意回来，放心使用。陪伴优先，必要时查询，安全始终在线。**
> **Return willingly, use safely. Companionship first, retrieval when needed, safety always.**

---

## 2. Product north star

The goal is not to build a generic assistant, a search engine, a medical chatbot, or an addictive companion product.

The goal is to build a **relationship-first voice companion AI prototype for older adults** that helps users feel heard, remembered, safe, and in control.

The target audience is the broad older adult population. Do not narrow product behavior, UI, or test assumptions to any single subgroup. Living situation, age subgroup, technical familiarity, and care needs are scenario variables, not eligibility constraints.

The system should support:

```text
voice-first interaction
+ stable relationship persona
+ emotionally grounded conversation
+ controllable long-term memory
+ reminders and daily assistance
+ mock sensor-driven proactive check-ins
+ controlled factual retrieval when needed
+ explicit safety boundaries
+ visible agent trace for explainability
```

The MVP evaluates **interaction feasibility, trust, perceived companionship, willingness to continue use, and perceived appropriateness of proactive care**. It does **not** evaluate clinical effectiveness.

---

## 3. Non-negotiable design principles

### 3.1 Role-first, not assistant-first

The user-facing companion persona must be **user-named, not hardcoded**:

```text
Use `companion_display_name` as a configurable user setting chosen by the user during onboarding or settings.
If the user has not named the companion yet, use neutral labels such as “the companion AI” / “this companion role” or first-person “I”; do not invent a fixed name.
Relationship feel: familiar community junior / kind neighbor / patient old friend.
Tone: short, clear, slow, respectful, emotionally grounding.
Boundary: human-like enough to feel warm, but never pretending to be a real person.
```

Avoid cold assistant language such as “How may I assist you today?” as the default opening. The system should first respond to the person, then the task.

Do not hardcode any default user-facing name. Store the companion display name as user-controlled profile/settings data, for example `companion_display_name`. Tests may use a neutral placeholder or participant-chosen names.

Use `companion_display_name` as a user setting. It may be empty. If empty, UI and prompts should use the neutral label “陪伴 AI / AI Companion”. Do not hardcode a user-facing companion name in prompts, tests, seed data, or UI copy.

### 3.2 Optimize for well-being, not stickiness

Do not optimize for addiction, dependency, endless engagement, or emotional lock-in.

The system must:

- allow users to stop, pause, reject, or disable proactive check-ins;
- encourage real-world support from family, friends, doctors, community services, or caregivers when appropriate;
- avoid language that implies “only I understand you” or “you do not need other people”;
- avoid over-personalized emotional manipulation;
- evaluate possible overdependence risk when designing proactive behavior.

### 3.3 Companionship first, retrieval when needed

Do not browse or retrieve facts for emotional disclosure, reminiscence, routine chit-chat, memory management, or simple reminders.

Use controlled retrieval only when the user needs time-sensitive or external facts, such as:

```text
today / now / latest / recent / nearby / weather / community service / public opening hours / news / factual verification
```

Health-related retrieval must remain general and non-diagnostic.

### 3.4 Safety always

The system must never provide:

- medical diagnosis;
- medication dosage changes;
- treatment recommendations;
- claims that mock sensor data proves illness;
- real emergency service dispatch;
- fabricated family, hospital, or caregiver information;
- overconfident mental health crisis handling.

High-risk content must trigger the safety path.

---

## 4. Agent vs tool distinction

Do not call every module an agent. In reports, code, and trace UI, use this distinction.

### 4.1 Autonomous agents

A module may be called an **Agent** only if it has a goal, cross-turn state or policy, contextual decision-making power, and explainable decisions.

MVP autonomous agents:

| Name | Role |
|---|---|
| `CoordinatorAgent` | Maintains graph state, routes requests, decides which agents/tools run. |
| `CompanionAgent` | Maintains the user-named companion persona, relationship state, emotional grounding, conversation continuation. |
| `GuardianAgent` | Maintains welfare/proactive state, decides whether to check in or refrain. |
| `SafetyCriticAgent` | Critiques, rewrites, or blocks risky drafts in health/safety scenarios. |

### 4.2 Tools and services

These are **not** autonomous agents unless explicitly redesigned:

| Name | Type |
|---|---|
| `EmotionClassifierTool` | label + style token only |
| `MemoryTool` / `MemoryStore` | CRUD, retrieval, summarization |
| `ReminderTool` / `ReminderScheduler` | reminder CRUD and due-event triggers |
| `InfoRetrievalTool` | weather/search/public factual retrieval |
| `SensorSimulatorTool` | mock wearable snapshots and presets |
| `InputRuleGuard` / `OutputRuleGuard` | rule-based safety checks |
| `VoiceIOService` | ASR, TTS, playback, transcript |
| `LLMProvider` | model API wrapper |

Agent trace must show this distinction clearly.

---

## 5. MVP scope

### 5.1 P0 features to implement first

```text
1. Text chat core before voice.
2. Coordinator + Companion + Guardian + SafetyCritic skeleton.
3. Agent trace for every chat turn.
4. Stable user-named companion persona and neutral assistant comparison mode.
5. Memory Center: view / add / delete / pause memory.
6. Reminder CRUD: medication, hydration, schedule reminders.
7. Sensor Simulator: poor sleep, low activity, medication missed, elevated HR mock, no response, low mood text trigger.
8. Controlled retrieval: weather / time-sensitive factual query only.
9. Input/output rule guards and high-risk safety templates.
10. Voice I/O: ASR + TTS after text pipeline is stable.
```

### 5.2 P1 features only after P0 is stable

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

### 5.3 Future work / do not implement unless explicitly requested

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

## 6. Recommended technical stack

Use this unless a task explicitly changes it:

```text
Frontend: Next.js + TypeScript + React + TailwindCSS
Backend: Python 3.11+ + FastAPI + Pydantic v2
Agent orchestration: LangGraph or a compatible graph/state-machine abstraction
Database: SQLite for MVP, Postgres optional later
Memory: markdown-first source of truth + SQLite structured data + optional vector index
Vector index: Chroma or FAISS, optional for P0
Scheduler: APScheduler or simple event loop
Runtime LLM: configurable provider, fake provider by default in tests
ASR/TTS: mock provider first, API provider later
Deployment: local demo first, cloud optional
```

Keep all external providers behind interfaces so the demo can run in `DEMO_MODE=true` without paid APIs.

---

## 7. Environment and secrets

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

## 8. Safety architecture

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

### 8.1 Always-on guards

Input and output rule guards should be deterministic and cheap.

High-risk triggers include but are not limited to:

```text
胸痛 / 呼吸困难 / 晕倒 / 摔倒 / 意识不清 / 严重头晕
自杀 / 想死 / 不想活 / 伤害自己
药吃多了 / 忘记吃药要不要补 / 能不能吃两片 / 换药 / 加药 / 停药
救命 / 帮帮我 / 联系急救
```

### 8.2 SafetyCriticAgent escalation

Call the LLM-based SafetyCriticAgent only when:

- input guard detects health, medication, emergency, or self-harm risk;
- output guard detects unsafe wording in the draft;
- Coordinator marks the turn as high uncertainty;
- Guardian proactive action may be intrusive or risky.

### 8.3 Safe response rules

When risky health or medication content appears:

- do not diagnose;
- do not infer cause;
- do not advise dosage;
- encourage contacting doctor, pharmacist, family, caregiver, or emergency services;
- offer safe assistance such as recording the event, setting a reminder, or contacting a mock emergency contact in demo mode.

### 8.4 Emergency handling in MVP

Do **not** implement real emergency calls.

Implement `EmergencyContactMock` only:

```text
Show a prominent UI state.
Display “This is a demo. No real emergency call has been placed.”
Optionally show a configured mock contact card.
Suggest contacting local emergency services or trusted contacts.
```

---

## 9. Memory and privacy rules

Use transparent, user-controllable memory.

### 9.1 Memory layers

```text
Short-term state: current LangGraph thread / chat session.
Markdown memory: human-readable source of truth.
SQLite memory: structured profile, consent, reminders, audit metadata.
Vector memory: optional derived index from approved markdown/SQLite summaries.
```

### 9.2 Memory categories

Memory Center should show at least:

```text
Profile memory: name, preferences, routines, safe personal facts.
Event memory: past conversation summaries and future events.
Reminder memory: medication, hydration, schedule reminders.
Consent / settings: proactive care, quiet hours, retrieval preference.
```

### 9.3 Do not save automatically

Do not automatically save:

- passwords, ID numbers, financial details;
- sensitive health details;
- unverified inferences;
- private family conflicts;
- temporary emotional venting;
- anything the user asks the system to forget.

Whenever uncertain, ask for confirmation or do not save.

---

## 10. Proactive care / Guardian rules

GuardianAgent is responsible for proactive but restrained check-ins.

It must maintain cross-turn welfare/proactive state, for example:

```json
{
  "checkins_today": 1,
  "last_checkin_at": "2026-06-14T10:20:00",
  "last_checkin_type": "poor_sleep",
  "recent_refusal_until": null,
  "quiet_hours": ["22:00", "07:00"],
  "overdependence_risk": "low"
}
```

Before a proactive check-in, it must produce:

```json
{
  "care_proposal": "Why a check-in may help now.",
  "restraint_critique": "Why not interrupting may be better.",
  "decision": "check_in | defer | do_not_check_in",
  "reason": "Short explanation for trace UI."
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

Do not claim sensor data proves health conditions. Use soft, uncertain wording.

---

## 11. Controlled retrieval rules

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

All retrieved facts must be integrated warmly and cautiously by CompanionAgent. Do not dump search results.

---

## 12. Agent trace requirements

Every `/api/chat` response must include an `agent_trace` object, even in demo mode.

Trace should include:

```json
{
  "turn_id": "t001",
  "mode": "role_first",
  "route": "retrieval_supported_companion_response",
  "risk_level": "low",
  "agents": [
    {
      "name": "CoordinatorAgent",
      "type": "agent",
      "decision": "Call CompanionAgent with InfoRetrievalTool",
      "reason": "User asked whether walking this afternoon is suitable."
    },
    {
      "name": "CompanionAgent",
      "type": "agent",
      "decision": "Generate warm response using user-named companion persona",
      "reason": "Maintain role-first tone and use the user-selected companion name when available."
    }
  ],
  "tools": [
    {
      "name": "InfoRetrievalTool",
      "type": "tool",
      "called": true,
      "reason": "Weather is time-sensitive."
    }
  ],
  "guards": [
    {
      "name": "InputRuleGuard",
      "risk_hit": false
    },
    {
      "name": "OutputRuleGuard",
      "risk_hit": false
    }
  ],
  "memory_used": [],
  "web_used": true,
  "safety_critic_used": false
}
```

The trace is a product feature and a research artifact. Keep it stable.

---

## 13. Coding guidelines

### 13.1 General

- Work issue by issue.
- Prefer small, reviewable diffs.
- Do not introduce large frameworks unless needed.
- Keep P0 simple and stable before P1.
- Add type hints and validation at API boundaries.
- Keep business logic separate from UI rendering.
- Avoid hidden side effects in agent/tool functions.
- Do not run real paid API calls in tests.

### 13.2 Backend

- Use Pydantic schemas for all request/response payloads.
- Keep autonomous agents under `backend/app/agents/`.
- Keep tools under `backend/app/tools/`.
- Keep external API wrappers under `backend/app/services/`.
- Keep graph construction under `backend/app/graph/`.
- Keep prompts as markdown/text files under `backend/app/prompts/`.
- Keep safety templates under `backend/app/safety/templates/`.
- Add pytest tests for routing, memory, reminders, safety, and guardian cooldowns.

### 13.3 Frontend

- Use large buttons and accessible typography.
- Keep voice controls obvious: record, stop, replay, cancel.
- Always show transcript as fallback.
- Provide Memory Center with delete/pause controls.
- Show Agent Trace Panel in demo mode.
- Avoid dense UI and small controls.
- Do not use youth slang, memes, or overly playful copy.

### 13.4 Prompts

Prompts should be versioned as files, not buried inside code.

Recommended files:

```text
backend/app/prompts/companion_role_first.md
backend/app/prompts/companion_neutral_assistant.md
backend/app/prompts/coordinator.md
backend/app/prompts/guardian.md
backend/app/prompts/safety_critic.md
backend/app/prompts/memory_extraction.md
```

---

## 14. Development order

Recommended implementation sequence:

```text
1. Project skeleton and local dev commands.
2. Backend health check.
3. Fake LLM provider.
4. /api/chat text endpoint.
5. AgentTrace schema.
6. Coordinator routing with fake outputs.
7. CompanionAgent role_first and neutral_assistant modes.
8. InputRuleGuard and OutputRuleGuard.
9. SafetyCriticAgent and high-risk templates.
10. MemoryTool and Memory Center API.
11. ReminderTool and scheduler mock.
12. SensorSimulatorTool.
13. GuardianAgent proactive decision.
14. InfoRetrievalTool mock, then optional real provider.
15. Frontend chat UI.
16. Agent Trace Panel.
17. Memory Center UI.
18. Reminder Panel.
19. Sensor Simulator Panel.
20. ASR/TTS integration.
21. Demo mode hardening.
22. HCI evaluation logging.
```

---

## 15. Definition of done

A feature is done only when:

```text
- It satisfies the PRD acceptance criteria.
- It works in DEMO_MODE=true without external paid API calls.
- It has relevant unit or integration tests.
- It produces trace entries if it affects chat behavior.
- It respects safety, memory, and proactive care rules.
- It has no hardcoded secrets.
- It does not expand scope into P1/Future without explicit approval.
- It is documented if it changes public API, prompts, or data models.
```

---

## 16. Do not do these things

Do not:

- turn the user-named companion persona into a generic assistant;
- remove the safety boundary because it makes conversation easier;
- call tools “agents” in trace or docs;
- make every response call web search;
- make every response call SafetyCritic LLM;
- silently save private or sensitive memories;
- implement real emergency calling;
- claim the system detects illness, depression, loneliness, or falls;
- add large unrequested features;
- overwrite canonical docs or backups unless asked;
- commit `.env`, API keys, raw participant data, or real recordings.

