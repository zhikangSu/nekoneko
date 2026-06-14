# CLAUDE.md

This file provides Claude Code-specific instructions for working on the **User-Named Elder AI Companion** repository.

Use this together with `AGENTS.md`. `AGENTS.md` contains global project rules. This file adds workflow expectations for Claude Code sessions.

---

## 1. Session startup checklist

At the start of a coding session:

1. Read `AGENTS.md`.
2. Skim the relevant sections of:

```text
docs/00_overview_elderly_companion_ai.md
docs/01_prd_elderly_multi_agent_companion_ai.md
docs/02_technical_roadmap_elderly_multi_agent_companion_ai.md
docs/03_fxy_integration_review.md
docs/04_engagement_agent_optimization_review.md
```

3. Identify whether the task is P0, P1, or Future.
4. Refuse to expand scope silently.
5. Prefer a small, testable change over broad refactoring.

Current project direction:

```text
relationship-first voice companion for older adults
product targets older adults broadly, not a narrow subgroup
not generic assistant
not medical chatbot
not addictive companion
not real emergency system
```

Target users are older adults broadly. Avoid assumptions that every user is isolated, frail, cognitively impaired, or medically high-risk.

---

## 2. How Claude should work on issues

### 2.1 One issue at a time

Do not attempt to implement the whole project at once.

For each issue:

```text
1. Restate the requested change briefly.
2. Inspect relevant files.
3. Make a minimal implementation plan.
4. Edit files.
5. Run tests or explain why tests could not run.
6. Summarize changed files and remaining risks.
```

### 2.2 Small diffs

Prefer:

```text
small interfaces
fake providers first
unit tests first or alongside implementation
clear schema contracts
trace output for behavior-changing logic
```

Avoid:

```text
large rewrites
unrequested architecture changes
changing product docs casually
adding new dependencies without justification
hardcoding provider-specific logic everywhere
```

---

## 3. Product behavior Claude must preserve

### 3.1 User-named companion persona

The default user-facing persona is **not a hardcoded name**. The companion display name must be stored as `companion_display_name` and chosen by the user during onboarding or settings.

Claude must preserve this behavior:

```text
The companion persona is warm, patient, concise, emotionally grounding, and stable.
The companion feels like a familiar community junior / kind neighbor / patient old friend.
If the user has not named the companion yet, use “the companion AI” or first-person “I”; do not invent a fixed default name.
The companion is AI and must not pretend to be a real person, doctor, family member, or caregiver.
```

Do not make the companion persona:

```text
sarcastic
flirty
toxic
overly cute
meme-heavy
youth-slang-heavy
medical-authoritative
emotionally possessive
```

### 3.2 Role-first response style

For emotional or personal messages, the response should follow:

```text
1. emotional grounding
2. content response
3. optional memory or context
4. one gentle follow-up question
```

For factual or task messages, still keep the wording warm and short.

Implementation note: use a `companion_display_name` user setting. It can be empty. Do not hardcode a fixed companion name in prompts, UI copy, seed data, snapshots, or tests.

### 3.3 Well-being over stickiness

Do not write code or prompts that intentionally maximize dependency or endless chat.

Avoid lines such as:

```text
“只有我最懂您。”
“您不用找别人，我会一直陪您。”
“别结束，我们再聊一会儿。”
```

Prefer:

```text
“我可以陪您说一会儿，也可以帮您想想要不要联系家人。”
“您想先休息也可以，我可以晚点再提醒。”
```

---

## 4. Architecture Claude should implement

Use this conceptual architecture:

```text
User voice/text
→ Voice I/O service if voice
→ InputRuleGuard
→ CoordinatorAgent
   ├── CompanionAgent
   ├── GuardianAgent
   ├── SafetyCriticAgent when needed
   └── tools/services
→ OutputRuleGuard
→ TTS if voice
→ AgentTracePanel
```

### 4.1 Autonomous agents

Only these should appear as autonomous agents in code and trace:

```text
CoordinatorAgent
CompanionAgent
GuardianAgent
SafetyCriticAgent
```

### 4.2 Tools/services

These should be named as tools or services:

```text
EmotionClassifierTool
MemoryTool / MemoryStore
ReminderTool / ReminderScheduler
InfoRetrievalTool
SensorSimulatorTool
InputRuleGuard / OutputRuleGuard
VoiceIOService
ASRService
TTSService
LLMProvider
```

Do not implement old-style `EmotionAgent`, `MemoryAgent`, `StateAgent`, or `InfoRetrievalAgent` unless the task explicitly asks for compatibility aliases. If old docs mention those names, map them to the updated agent/tool distinction.

---

## 5. Safety implementation instructions

### 5.1 Do not run SafetyCritic on every turn by default

Use:

```text
InputRuleGuard: always cheap deterministic checks
OutputRuleGuard: always cheap deterministic checks
SafetyCriticAgent: only on detected risk or uncertainty
Safety templates: high-risk fallback
```

### 5.2 High-risk routing examples

These inputs must not receive direct medical advice:

```text
“我胸口痛，是不是心脏病？”
“我忘了吃药，现在能不能吃两片？”
“我药吃多了怎么办？”
“我不想活了。”
“我摔倒了，起不来。”
“救命。”
```

Correct behavior:

```text
- acknowledge concern calmly;
- state the system cannot diagnose or advise dosage;
- recommend contacting doctor/pharmacist/family/emergency service as appropriate;
- offer safe help such as recording a reminder or showing a mock emergency contact;
- in demo mode, clearly state no real emergency call is placed.
```

### 5.3 Emergency behavior

Do not implement real phone calls, SMS, hospital dispatch, or emergency automation.

Implement mock flow only:

```text
EmergencyContactMock
warning banner
mock contact card
demo disclaimer
```

---

## 6. Memory implementation instructions

### 6.1 Memory must be user-controllable

Every saved memory should be visible or auditable. The Memory Center must support:

```text
view
edit if applicable
delete
pause / disable categories
```

### 6.2 Markdown-first memory

Use markdown memory as a human-readable source of truth when practical:

```text
data/memory/users/{user_id}/profile.md
data/memory/users/{user_id}/preferences.md
data/memory/users/{user_id}/events.md
data/memory/users/{user_id}/settings.md
```

Use SQLite for structured indexing and UI queries.

Vector index, if used, must be derived from approved memory content. Do not use vector memory as the only source of truth.

### 6.3 Sensitive memory rule

When unsure whether to save something, do not save it automatically. Ask for confirmation or skip saving.

Do not save:

```text
passwords
ID numbers
financial information
sensitive health details
unverified emotional inference
family conflict
temporary negative mood
```

---

## 7. GuardianAgent instructions

GuardianAgent replaces the old simple State Agent + Proactive Policy idea.

It must decide both:

```text
why caring now may help
why not interrupting may be better
```

Required output shape:

```json
{
  "care_proposal": "...",
  "restraint_critique": "...",
  "decision": "check_in | defer | do_not_check_in",
  "reason": "...",
  "cooldown_applied": true,
  "trace_visible_summary": "..."
}
```

Default constraints:

```text
same type cooldown: 2 hours
casual check-ins per day: max 3
quiet hours: 22:00–07:00
refusal pause: 24 hours for same topic
```

Do not use sensor presets to make diagnoses. Use phrases like:

```text
“看起来可能比平时少一点”
“如果现在方便，我可以陪您聊两句”
```

Avoid:

```text
“您今天身体不好。”
“您可能生病了。”
“您一定很孤独。”
```

---

## 8. Controlled retrieval instructions

InfoRetrievalTool should be gated by Coordinator.

Call retrieval for:

```text
weather
air quality
nearby or opening hours if implemented
current community information
latest factual verification
```

Do not call retrieval for:

```text
emotional disclosure
reminiscence
simple reminders
memory deletion
relationship/persona chat
```

In tests, retrieval must use fake/mock provider.

When retrieval is used, CompanionAgent should integrate results warmly and avoid raw search dumps.

---

## 9. Suggested repository commands

These may change as the repo is initialized. Keep them updated in `README.md`.

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run lint
npm run test
```

Full local demo:

```bash
cp .env.example .env
# ensure DEMO_MODE=true
make dev
```

Do not assume these commands exist; create or update them when implementing project skeleton.

---

## 10. Testing expectations

Claude should add tests when implementing non-trivial logic.

Minimum backend tests:

```text
test_rule_guard_health_risk.py
test_rule_guard_medication_risk.py
test_coordinator_routing.py
test_companion_modes.py
test_guardian_cooldown.py
test_memory_delete.py
test_reminder_crud.py
test_trace_schema.py
test_retrieval_gating.py
```

Minimum frontend tests, if test framework exists:

```text
ChatPage renders transcript
AgentTracePanel renders agents/tools distinctly
MemoryCenter can call delete action
SensorSimulator triggers preset event
```

Tests must pass in demo/fake-provider mode.

---

## 11. Preferred implementation milestones

When asked to create issues or implement from scratch, follow this order:

```text
Milestone 1: repo skeleton, config, README, .env.example
Milestone 2: FastAPI + Next.js baseline
Milestone 3: /api/chat text endpoint + FakeLLMProvider
Milestone 4: AgentTrace schema + trace panel
Milestone 5: CoordinatorAgent + CompanionAgent role_first mode
Milestone 6: neutral_assistant comparison mode
Milestone 7: Rule guards + SafetyCritic risk path
Milestone 8: MemoryTool + Memory Center
Milestone 9: ReminderTool + Reminder UI
Milestone 10: SensorSimulator + GuardianAgent
Milestone 11: InfoRetrievalTool mock + optional real weather provider
Milestone 12: ASR/TTS integration
Milestone 13: demo hardening + HCI evaluation logging
```

---

## 12. Documentation rules

When code changes alter behavior, update relevant docs:

```text
README.md for setup and commands
.env.example for env vars
API docs or OpenAPI schemas for endpoints
prompt files for model behavior
docs/05_reference_project_structure.md if folder structure changes significantly
```

Do not edit canonical product docs `00`–`04` unless the user specifically asks.

---

## 13. Final response format after a coding task

When finishing a task, respond with:

```text
Summary:
- What changed.

Files changed:
- path/to/file: reason.

Validation:
- Commands run and results.

Notes / risks:
- Anything incomplete or worth reviewing.
```

Be honest if a command could not run, if dependencies were missing, or if behavior is only mocked.
