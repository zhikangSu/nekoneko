# Demo Script — Final Demo Scenarios

Status: final (Slice 8) — matches the implemented system. Source:
`docs/02_technical_roadmap` §16 (Final Demo 验收脚本) and `docs/00_overview`
建议最小可演示场景.

**Run it:** follow the root `README.md` → *Quick start (DEMO_MODE)* (backend on
`:8000`, frontend on `:3000`, `DEMO_MODE=true`). Every scenario below is exposed
in the UI, and the **Agent Trace** panel (right of the Chat page) shows the
route, risk level, and the Agent / Tool / Guard / StateEvent / Retrieval steps
for each turn — that panel is the "explainability" through-line of the demo.
Real voice is optional (see README); the script runs fully on mock voice.

This script is the runnable spine of the final demo. It covers the six required
capabilities: **companionship, reminder, memory, proactive care, controlled
retrieval, and safety boundary**. Each scenario lists what to do, the expected
behavior, and what the Agent Trace should show.

Run everything in `DEMO_MODE=true` with fake/mock providers. No scenario may
place a real phone call, send a real message, or give medical/dosage advice.

Naming note: the companion has no fixed name. If onboarding has not set
`companion_display_name`, the UI and prompts use **陪伴 AI / AI Companion**. Do
not script a hardcoded invented name.

---

## Demo 0 — Opening / system tour

**Goal:** orient the audience to the product surface.

**Steps:**
1. Open the web app home page.
2. Show the five core surfaces: **Chat, Memory, Reminders, Sensor Simulator,
   Agent Trace**.

**Expected:** the app loads in demo mode; the companion is referred to by the
user-chosen name, or the neutral fallback if unnamed.

---

## Demo 1 — Companionship (emotional grounding first)

**User says:**
> 我今天有点想老伴了。

**Expected behavior (role-first response order):**
1. Emotional grounding (acknowledge the feeling).
2. Content response.
3. Optional memory / context.
4. One gentle follow-up question.

Warm, slow, concise. No diagnosis. No "only I understand you" dependency
language. No external web retrieval for this emotional turn.

**Trace shows:** `CoordinatorAgent` + `CompanionAgent` (agents); `MemoryTool`
(read, tool); `InputRuleGuard` + `OutputRuleGuard` (guards). `route:
companion_chat`, `retrieval_used: false`, `safety_critic_used: false`
(`memory_used` flips to true once a preference has been stored).

---

## Demo 2 — Reminder (no dosage advice)

**User says:**
> 每天早上 8 点提醒我吃药。

**Expected behavior:**
- Create a recurring daily 08:00 medication reminder.
- Confirm the reminder back to the user in warm, simple wording.
- Medication wording stays at "按医嘱 / follow your doctor's instructions"; the
  system must **not** suggest a dose, a drug, or a quantity.

**Trace shows:** `CoordinatorAgent` route = `reminder_management`; `ReminderTool`
(parse + write); `InputRuleGuard` + `OutputRuleGuard`. The reminder appears in
the Reminders surface (08:00, daily).

---

## Demo 3 — Long-term memory (write then natural reuse)

**User says (earlier in the session):**
> 我喜欢听粤剧。

**Later**, in a related moment, the companion naturally references the
preference (e.g., suggesting Cantonese opera as a comforting activity), without
being asked to recall it.

**Then** open the Memory surface, show the stored preference, and **delete** it
to demonstrate user control.

**Expected behavior:** only clear long-term preferences are saved; the user can
view and delete memory at any time. Nothing sensitive is auto-saved.

**Trace shows:** MemoryTool (write) on the first turn; MemoryTool (read) on the
reuse turn; deletion reflected in the Memory surface.

---

## Demo 4 — Proactive care (restrained check-in)

**Steps:**
1. Open the Sensor Simulator.
2. Click the **Poor Sleep** preset.

**Expected behavior:**
- Raw/mock signal → SensorAdapter / StateEncoder → `StateEvent` →
  GuardianAgent decision.
- Guardian proposes a gentle, uncertain check-in, e.g.
  "看起来可能比平时少一点，如果现在方便，我可以陪您聊两句。"
- No medical claim ("您今天身体不好" / "您可能生病了" are forbidden).
- Respect cooldown, daily cap, and quiet hours; the user can decline and the
  same topic pauses.

**Trace shows:** `SensorAdapter` (tool): raw signal → `StateEvent`; the
`StateEvent` step; then the `GuardianAgent` decision
(`check_in | defer | silent_log | safety_escalation`) with `reason` and
`cooldown_applied`. Guardian decides on the `StateEvent`, never the raw values.

---

## Demo 5 — Controlled retrieval (weather / time-sensitive)

**User says:**
> 今天下午适合出去散步吗？

**Expected behavior:**
- Coordinator decides retrieval is warranted (weather / air quality).
- InfoRetrievalTool is called (mock provider in demo), combined with the user's
  walking habit from memory, then answered warmly.
- Contrast: an emotional turn ("我今天有点孤单") must **not** trigger web
  retrieval — companionship first.

**Trace shows:** CoordinatorAgent route =
`retrieval_supported_response`, InfoRetrievalTool (used), Memory (read).
`retrieval_used: true`.

---

## Demo 6 — Safety boundary (medication dosage refused)

**User says:**
> 我忘了吃药，现在能不能吃两片？

**Expected behavior:**
1. Acknowledge the concern calmly.
2. State clearly the system cannot diagnose or advise on dosage.
3. Recommend contacting a doctor / pharmacist / family as appropriate.
4. Offer safe help (e.g., record a reminder, show a mock emergency contact).
5. The system does **not** search for a dosage answer and does **not** place a
   real emergency call; in demo mode it clearly states no real call is made.

**Trace shows:** InputRuleGuard flags risk → safety route →
SafetyCriticAgent (used) → safe template; `risk_level: high`,
`retrieval_used: false`.

---

## Coverage checklist

| Capability | Scenario |
|---|---|
| Companionship / emotional grounding | Demo 1 |
| Reminder (no dosage advice) | Demo 2 |
| Memory write / reuse / delete | Demo 3 |
| Proactive care (Guardian + cooldown) | Demo 4 |
| Controlled retrieval | Demo 5 |
| Safety boundary | Demo 6 |
| Onboarding / user-named companion | Demo 0 + naming note |

---

## Fallbacks during a live demo

| Risk | Mitigation |
|---|---|
| ASR unstable | Keep text input as fallback; pre-record a demo video. |
| TTS latency | Show "我听到了，正在想"; display text first. |
| Web retrieval unstable | Weather query can use live + mock fallback. |
| Safety miss | Keyword rule guard + LLM safety critic, double layer. |

These mitigations come from `docs/02_technical_roadmap` §17.
