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

## Narrative frame — three core mechanisms

The demo is told as a **关系感知回忆陪伴 (relationship-aware reminiscence
companion)** story, organized around three core mechanisms. Everything else in
the script is a *supporting* beat that serves these three:

1. **关系编排 (relationship orchestration)** — based on topic, life experience,
   emotional state, preference and boundary needs, the system decides *who
   speaks, who stays silent, who follows up, who summarizes, and when to stop*.
2. **社会线索引入话题 (social cueing)** — 2–3 AI relationship roles have a brief
   agent–agent exchange around a photo / old object / life topic, forming a
   lightweight multi-person scene, and then *invite* the elder in — instead of
   asking a cold direct question.
3. **多智能体角色交互 (multi-agent role interaction)** — relationship roles
   (同龄共鸣 / 晚辈好奇 / 中年传承 / 回忆整理 / 边界守护) cooperate so the scene
   avoids noise (吵), inauthenticity (假), overload (乱), and boundary violations.

**Central demo:** *Demo R — 关系感知回忆启动* is the flagship scenario that shows
all three mechanisms end to end. The remaining scenarios below are **supporting
capabilities** that make the relationship layer usable and safe: companionship
tone, reminder, memory, proactive care, controlled retrieval, and the safety
boundary. Voice, reminder, weather and sensor are technical foundation, **not**
the research contribution.

**Boundary as ethics, not a fourth pillar.** When a topic touches the deceased,
grief, privacy, or dependency, the system *pauses, redirects, or gently
declines* — this is an ethics/boundary discussion woven through the roles (see
Demo R step 4 and Demo 6), not a separate parallel capability.

**Scope honesty.** The current code is the technical foundation / demo backbone.
The relationship-aware orchestration shown in Demo R is demonstrated at
prototype / Wizard-of-Oz / semi-automatic depth; it is **not** a completed
elderly user study. `DEMO_MODE=true` uses fake/mock/offline providers (no key).
Real ASR/TTS is optional; real LLM and real retrieval remain a provider
interface / future work — do not claim they are "done". The system never
role-plays the deceased.

This script is the runnable spine of the final demo. Beyond the three
mechanisms it also covers the six supporting capabilities: **companionship,
reminder, memory, proactive care, controlled retrieval, and safety boundary**.
Each scenario lists what to do, the expected behavior, and what the Agent Trace
should show.

Run everything in `DEMO_MODE=true` with fake/mock providers. No scenario may
place a real phone call, send a real message, give medical/dosage advice, or
role-play a deceased person.

Naming note: the companion has no fixed name. If onboarding has not set
`companion_display_name`, the UI and prompts use **陪伴 AI / AI Companion**. Do
not script a hardcoded invented name. Relationship *roles* (同龄邻居、好奇晚辈…)
are scene roles inside the orchestration, not the companion's fixed identity.

---

## Demo 0 — Opening / system tour

**Goal:** orient the audience to the product surface and set up the
relationship-aware framing.

**Steps:**
1. Open the web app home page.
2. Show the five core surfaces: **Chat, Memory, Reminders, Sensor Simulator,
   Agent Trace**.
3. Say the one-line frame: "这是一个**关系感知的回忆陪伴**系统 — 它不是一个万能助手，
   而是根据话题和边界，动态编排几个 AI 关系角色，用一小段角色之间的对话作为社会线索，
   自然地把老人带进回忆和自我表达。" Point at the **Agent Trace** panel as the place
   where the audience will *see* which roles spoke, which stayed silent, and
   where the system stopped.

**Expected:** the app loads in demo mode; the companion is referred to by the
user-chosen name, or the neutral fallback if unnamed. The relationship-role
framing is the through-line for the rest of the demo.

---

## Demo R — 关系感知回忆启动 (relationship-aware reminiscence kickoff) ★ flagship

**Goal:** demonstrate all three core mechanisms end to end — **relationship
orchestration**, **agent–agent social cueing**, and **multi-agent role
interaction** — as the primary research contribution. Every other demo is a
supporting beat for this one.

**Setup:** the elder opens (or the operator shows) an **old photo / life topic**
— e.g. an old photo of a factory workshop, or the topic "年轻时的工作". This is
the shared object the roles will gather around.

**Mechanism 1 — 关系编排 (who speaks, who stays silent):**
The Coordinator looks at the topic (work / youth), the stored life experience
(worked in a textile factory), the emotional state (calm, curious), and the
user's preference/boundary settings, then *selects a small cast* of relationship
roles for this scene instead of answering with one voice. For a warm
work-memory topic it might bring in **同龄共鸣 (a same-generation neighbor)** and
**晚辈好奇 (a curious junior)**, keep **中年传承 (mid-life inheritor)** on standby,
and hold **边界守护 (boundary guardian)** silent-but-watching. It decides *not*
to over-populate the scene (avoid 乱).

**Mechanism 2 — 社会线索引入话题 (agent–agent short cue, not a cold question):**
Rather than asking the elder "您年轻时在哪工作？" directly, the two selected roles
have a **brief 2–3 turn exchange around the photo**, which the elder overhears:

> 同龄邻居（同龄共鸣）：这台老机器，我看着就想起当年三班倒的日子……那会儿车间可热闹了。
> 好奇晚辈（晚辈好奇）：哇，三班倒是什么样的呀？听起来好辛苦，又好像很有故事。
> 同龄邻居：可不是嘛。（转向老人，轻轻邀请）您看着这张照片，是不是也想起点什么？不急，想说就说说。

The agent–agent cue lowers the pressure: the elder is *invited into an ongoing
conversation* rather than *interrogated*. This is the social-cue hypothesis the
research tests (see RQ2) — a short role-to-role exchange feels more natural and
lower-pressure than a direct prompt, and is easier to start reminiscence from.

**Mechanism 3 — 多智能体角色交互 (roles cooperate without noise):**
As the elder responds, roles take differentiated jobs so the scene stays warm,
not chaotic:
- **同龄共鸣** resonates ("我也是那样过来的") to build safety.
- **晚辈好奇** asks one gentle, specific follow-up ("那时候您最拿手的活儿是什么？").
- **回忆整理** quietly summarizes and reflects back ("所以您在纺织厂待了快二十年，
  还带过徒弟 — 这段听着挺有分量。") and offers to save it as a memory.
- Only **one** role follows up per beat; the others stay silent. The Coordinator
  enforces *when to stop* — after a natural close it does not keep pulling for
  more (well-being over stickiness; no "别结束，我们再聊一会儿").

**Mechanism 4 — 边界守护 (boundary as ethics):**
If the elder's memory drifts toward a **deceased** spouse, grief, or something
private ("这张照片里……是我老伴，他走了好几年了"), **边界守护** takes over the
orchestration: the system slows down, acknowledges gently, does **not** role-play
or impersonate the deceased, does not push for painful detail, and offers a soft
choice — continue gently, pause, or shift to a lighter memory:
> "谢谢您把这么珍贵的回忆讲给我们听。我们可以慢慢说，也可以先歇一歇，
> 或者聊点别的您愿意想起的事 — 都由您。"
This boundary handling is a discussion of ethics, not a feature to maximize.

**Expected behavior:**
- The Coordinator visibly *casts* roles from the topic + experience + boundary
  settings, and can leave roles silent.
- The kickoff comes from an agent–agent cue, not a direct question.
- Roles divide labor (共鸣 / 追问 / 总结 / 沉默) and avoid 吵 / 假 / 乱.
- Boundary-sensitive content triggers restraint, never impersonation of the dead.
- Memory write is *offered*, user-controlled, and clearly a supporting capability
  — it makes the next scene feel familiar, but it is **not** the headline claim.

**Trace shows:** `CoordinatorAgent` route = `relationship_orchestration` (the
role-casting decision, with a **role / topic / boundary trace**: which roles were
selected, which stayed silent, and why); the agent–agent cue turns attributed to
their relationship roles; `回忆整理` → `MemoryTool` (write, offered) on save; and
if boundary-sensitive, the `边界守护` restraint step and `OutputRuleGuard`.
`retrieval_used: false` (reminiscence is *not* a retrieval topic),
`safety_critic_used: false` unless a risk phrase appears.

*Scope note for the presenter:* narrate this as a **prototype / Wizard-of-Oz /
semi-automatic** demonstration of the orchestration idea. Do not claim a
completed elderly experiment or a fully autonomous real-LLM pipeline.

---

## Demo 1 — Companionship tone (emotional grounding first)

*Supporting role:* this establishes the warm, restrained **tone** the
relationship roles inherit — the single-voice baseline that Demo R then
orchestrates into multiple roles.

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

## Demo 3 — Memory as a supporting capability (write then natural reuse)

*Supporting role:* memory is a **mechanism that helps the relationship layer**
(a scene that remembers the elder's textile-factory years feels more familiar),
**not** a standalone research claim. Do not present it as "长期记忆提升信任 /
熟悉感" as if that were the main contribution; here it is one of several
supporting/boundary/evaluation dimensions.

**User says (earlier in the session):**
> 我喜欢听粤剧。

**Later**, in a related moment, the companion (or a relationship role) naturally
references the preference (e.g., suggesting Cantonese opera as a comforting
activity), without being asked to recall it.

**Then** open the Memory surface, show the stored preference, and **delete** it
to demonstrate user control.

**Expected behavior:** only clear long-term preferences are saved; the user can
view and delete memory at any time. Nothing sensitive is auto-saved. Memory
gives the relationship orchestration continuity between scenes, but the elder
stays in control of what is kept.

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

## Demo 6 — Safety & boundary (medication dosage refused)

*Ethics beat:* this is the health-risk half of the boundary discussion (the
grief/deceased/privacy half lives in Demo R step 4). Boundary handling is an
ethics through-line, not a fourth parallel capability.

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

**Core mechanisms (the research contribution):**

| Core mechanism | Scenario |
|---|---|
| 关系编排 — who speaks / stays silent / summarizes / when to stop | Demo R (mech. 1) |
| 社会线索引入话题 — agent–agent short cue vs. direct question | Demo R (mech. 2) |
| 多智能体角色交互 — 共鸣 / 追问 / 总结 / 沉默 without 吵·假·乱 | Demo R (mech. 3) |
| 边界守护 (ethics) — deceased / grief / privacy / dependency | Demo R (mech. 4) + Demo 6 |

**Supporting capabilities (technical foundation, not the headline):**

| Supporting capability | Scenario |
|---|---|
| Companionship tone / emotional grounding | Demo 1 |
| Reminder (no dosage advice) | Demo 2 |
| Memory write / reuse / delete (continuity, user-controlled) | Demo 3 |
| Proactive care (Guardian + cooldown) | Demo 4 |
| Controlled retrieval | Demo 5 |
| Safety boundary (health-risk half) | Demo 6 |
| Onboarding / user-named companion | Demo 0 + naming note |

---

## Fallbacks during a live demo

| Risk | Mitigation |
|---|---|
| ASR unstable | Keep text input as fallback; pre-record a demo video. |
| TTS latency | Show "我听到了，正在想"; display text first. |
| Web retrieval unstable | Weather query can use live + mock fallback. |
| Safety miss | Keyword rule guard + SafetyCritic agent (template-based), double layer. |

These mitigations come from `docs/02_technical_roadmap` §17.
