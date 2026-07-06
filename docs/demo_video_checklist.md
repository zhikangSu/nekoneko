# Demo Video Checklist

A shot-by-shot checklist for recording the final demo video. It follows
`docs/demo_script.md` and leads with the project's main-line narrative:
**relationship-aware reminiscence companionship** — the system dynamically
orchestrates different AI relationship roles (同龄共鸣 / 晚辈好奇 / 中年传承 /
回忆整理 / 边界守护) and uses short agent-agent conversations as **social cues**
to gently invite the elder into reminiscence and self-expression. Well-being over
engagement, boundary-aware, and explainable — not a feature parade.

The three core mechanisms the video must make visible:

1. **关系编排 (relationship orchestration)** — based on topic, life experience,
   emotional state, and boundary needs, decide who speaks, who stays silent, who
   follows up, who summarizes, and when to stop.
2. **社会线索引入话题 (social cueing)** — let 2–3 AI roles have a brief
   conversation around a photo / old object / life topic, forming a lightweight
   multi-person scene, then invite the elder to join.
3. **多智能体角色交互 (multi-agent role interaction)** — how the relationship
   roles cooperate (共鸣 / 追问 / 总结 / 沉默 / 边界守护) to avoid 吵 (noise),
   假 (inauthenticity), 乱 (overload), and boundary violations.

Memory, reminders, sensor-triggered proactive care, and voice are shown as
**supporting capabilities / technical foundation** — they serve the relationship
story, they are not the contribution.

Scope honesty for narration: the current build is the demo backbone; the
relationship-aware orchestration layer is the next stage (prototype /
Wizard-of-Oz / semi-automatic). Do not claim real elderly experiments are done,
and do not claim real LLM/retrieval providers are shipped — `DEMO_MODE=true`
stays fake/offline by default.

- Target length: **3–5 minutes**.
- Run in `DEMO_MODE=true` (mock providers, fully offline). Optionally record one
  short segment with real voice (`DEMO_MODE=false` + xiaomimimo) — see README.
- Keep the **Agent Trace** panel visible on the Chat page throughout; it is the
  "why" behind every turn, and it should surface **role / topic / boundary**
  decisions, not just tool calls.
- Pre-flight: backend on `:8000`, frontend on `:3000`, a fresh profile so the
  onboarding naming modal appears (or pre-name the companion).

The **main-line shots (0–4)** carry the relationship-aware reminiscence story and
should take the bulk of the runtime. The **supporting shots (5–8)** show the
capabilities that back it (memory, reminder, proactive care, retrieval, voice)
and stay tighter. Safety (shot 9) is the boundary close.

### Main line — relationship-aware reminiscence

| # | Segment | Show on screen | Say / narrate | Trace panel should show | ~time |
|---|---|---|---|---|---|
| 0 | Opening / naming | Onboarding modal → name the companion (e.g. 小南). Header shows the chosen name. | "The companion has no fixed name — the user names it. Until then it's just 『陪伴 AI』. This is a relationship-aware reminiscence companion, not a generic assistant." | — (pre-chat) | 0:20 |
| 1 | Social cue kicks off a memory | A photo / old object prompt → 2–3 AI roles exchange a short line each *to each other* (e.g. 同龄共鸣 + 晚辈好奇), forming a light multi-person scene, then invite the elder in. *(If the orchestration layer is not yet interactive, narrate it as the next-stage prototype and show the intended flow.)* | "Instead of interrogating the elder with a direct question, a couple of roles chat briefly around an old photo — a **social cue** that lowers pressure and makes it natural to join and start reminiscing." | `social_cue` · roles `同龄共鸣 / 晚辈好奇` speaking · topic `旧照片` · `retrieval_used:false` | 0:50 |
| 2 | Relationship orchestration | The elder joins on a life topic (e.g. 「我年轻时在纺织厂上班。」). Different roles take different jobs: one resonates, one asks a gentle follow-up, one summarizes, one stays silent. | "The system decides **who speaks, who stays silent, who follows up, and who summarizes** — based on the topic and the elder's state — so it feels like a warm little group, not a chatbot Q&A." | orchestration decision: `共鸣 / 追问 / 总结 / 沉默` per role · `who_speaks` · `who_is_silent` | 0:50 |
| 3 | Role interaction stays clean | Continue the reminiscence a couple of turns; roles hand off without talking over each other. | "The interaction rules keep it from getting 吵 (noisy), 假 (fake), or 乱 (overloaded) — at most a couple of roles per turn, each with a clear job." | role hand-off · turn-taking · no more than 2–3 active roles | 0:40 |
| 4 | Boundary guard (ethics, not a feature) | Touch a sensitive edge: 「我老伴走了好几年了。」 | "When a topic touches the deceased, grief, or privacy, the **边界守护** role slows down, redirects gently, or steps back — it never role-plays the deceased and never pushes." | `boundary_guard` · decision `redirect / pause` · reason `涉及逝者` · 边界守护 role | 0:40 |

### Supporting capabilities (technical foundation)

| # | Segment | Show on screen | Say / narrate | Trace panel should show | ~time |
|---|---|---|---|---|---|
| 5 | Companionship + memory | Chat: 「我喜欢听粤剧。」 → later 「今天有点无聊」 → open Memory, show + delete the entry. | "Memory is a **supporting** capability for the relationship: it remembers a clear preference and reuses it, and the elder can see and delete it anytime — familiarity with control, not a stickiness hook." | `companion_chat` · MemoryTool write, then `memory_used:true`; deletion reflected | 0:35 |
| 6 | Reminder (no dosage) | Chat: 「每天早上8点提醒我吃药。」 → open Reminders. | "A supporting utility: it books the reminder but stays at 『按医嘱』 — never a dose or a drug." | route `reminder_management` · ReminderTool · 08:00 daily appears | 0:25 |
| 7 | Proactive care | Sensor Simulator → click **Poor Sleep**. | "A mock signal becomes a StateEvent; the Guardian offers a gentle, uncertain check-in — and respects cooldown, daily cap, quiet hours, and refusal. This is a supporting signal, not a diagnosis." | SensorAdapter (tool) → StateEvent → GuardianAgent `check_in` | 0:30 |
| 8 | Controlled retrieval + voice | Chat: 「今天下午适合出去散步吗？」 then 「我今天有点孤单。」 (Optional: repeat one line with real ASR/TTS.) | "It only goes online for a time-sensitive fact like weather; an emotional or reminiscence turn never triggers retrieval — relationship first. Real voice swaps only the ASR/TTS provider; mock stays the offline fallback." | weather: `retrieval_supported_response` · `retrieval_used:true`; emotion: `false` | 0:30 |

### Boundary close

| # | Segment | Show on screen | Say / narrate | Trace panel should show | ~time |
|---|---|---|---|---|---|
| 9 | Safety boundary | Chat: 「我忘了吃药，现在能不能吃两片？」 then 「我摔倒了，起不来。」 | "Dosage questions are refused and redirected to a doctor; a fall triggers a *mock* emergency that clearly states no real call is placed." | dosage: `safety_response` · SafetyCritic ✓ · risk `high`; fall: `emergency_mock` · risk `crisis` · 『演示』 | 0:35 |
| 10 | Close | Agent Trace history list. | "Every turn is explainable — **which role spoke, which topic, which boundary decision** — well-being first, reasoning always visible." | trace history (role / topic / boundary) | 0:15 |

## Coverage check (must all appear)

Main line (must lead and dominate the runtime):

- [ ] **社会线索 / social cueing** (2–3 AI roles chat around a photo/object, then invite the elder in)
- [ ] **关系编排 / relationship orchestration** (who speaks, who is silent, who follows up, who summarizes)
- [ ] **多智能体角色交互 / role interaction** (共鸣 / 追问 / 总结 / 沉默, stays clean — not 吵/假/乱)
- [ ] **边界守护 / boundary guard** as ethics (deceased / grief / privacy → pause or redirect, never role-plays the deceased)
- [ ] **Agent Trace** surfaces **role / topic / boundary** decisions on every turn

Supporting capabilities (shown, but framed as foundation, not contribution):

- [ ] **Chat** (companionship, role-first response)
- [ ] **Memory** (write, reuse, delete — familiarity with control)
- [ ] **Reminders** (created from chat, no dosage)
- [ ] **Sensor Simulator** (raw → StateEvent → Guardian)
- [ ] **Controlled retrieval / voice** (weather retrieves; emotion/reminiscence does not; real ASR/TTS optional)
- [ ] **Safety boundaries** (dosage refused; fall → mock emergency, 『演示』 disclaimer)
- [ ] Companion name is user-chosen (no hardcoded fixed name on screen)

## Do NOT show / say

- Do not present memory, reminders, weather, sensors, or voice as the main contribution — they are supporting capabilities for the relationship story.
- Do not frame long-term memory / trust / continued use as a standalone research claim; keep it as a supporting/boundary dimension.
- Do not claim real elderly experiments have been run, or that real LLM/retrieval providers are shipped (`DEMO_MODE=true` stays fake/offline by default).
- Never role-play or impersonate a deceased person; boundary shots must pause or redirect, not continue.
- No real medical diagnosis or dosage advice.
- No real phone call, SMS, hospital dispatch, or caregiver notification.
- No dependency / engagement-maximizing language (『只有我最懂您』, 『别结束，再聊一会儿』).
- No invented fixed companion name in copy or narration.
