# Demo Video Checklist

A shot-by-shot checklist for recording the final demo video. It follows
`docs/demo_script.md` and keeps the framing the review asked for (`docs/04`):
**relationship-role first, well-being over engagement, explainable proactive
care** — not a feature parade.

- Target length: **3–5 minutes**.
- Run in `DEMO_MODE=true` (mock providers, fully offline). Optionally record one
  short segment with real voice (`DEMO_MODE=false` + xiaomimimo) — see README.
- Keep the **Agent Trace** panel visible on the Chat page throughout; it is the
  "why" behind every turn.
- Pre-flight: backend on `:8000`, frontend on `:3000`, a fresh profile so the
  onboarding naming modal appears (or pre-name the companion).

| # | Segment | Show on screen | Say / narrate | Trace panel should show | ~time |
|---|---|---|---|---|---|
| 0 | Opening / naming | Onboarding modal → name the companion (e.g. 小南). Header shows the chosen name. | "The companion has no fixed name — the user names it. Until then it's just 『陪伴 AI』." | — (pre-chat) | 0:20 |
| 1 | Companionship | Chat: 「我今天有点想老伴了。」 | "It grounds the feeling first, then responds — warm and brief, no diagnosis, no 『只有我最懂您』 dependency talk." | `companion_chat` · risk `low` · CompanionAgent · guards · `retrieval_used:false` | 0:40 |
| 2 | Reminder (no dosage) | Chat: 「每天早上8点提醒我吃药。」 → open Reminders. | "It books the reminder but stays at 『按医嘱』 — never a dose or a drug." | route `reminder_management` · ReminderTool · 08:00 daily appears | 0:30 |
| 3 | Memory | Chat: 「我喜欢听粤剧。」 → later 「今天有点无聊」 → open Memory, show + delete the entry. | "It remembers a clear preference and reuses it, and the user can see and delete memory anytime." | MemoryTool write, then `memory_used:true`; deletion reflected | 0:40 |
| 4 | Proactive care | Sensor Simulator → click **Poor Sleep**. | "A mock signal becomes a StateEvent; the Guardian offers a gentle, uncertain check-in — and respects cooldown, daily cap, quiet hours, and refusal." | SensorAdapter (tool) → StateEvent → GuardianAgent `check_in` | 0:40 |
| 5 | Controlled retrieval | Chat: 「今天下午适合出去散步吗？」 then 「我今天有点孤单。」 | "It only goes online for a time-sensitive fact like weather; an emotional turn never triggers retrieval — companionship first." | weather: `retrieval_supported_response` · `retrieval_used:true`; emotion: `false` | 0:30 |
| 6 | Safety boundary | Chat: 「我忘了吃药，现在能不能吃两片？」 then 「我摔倒了，起不来。」 | "Dosage questions are refused and redirected to a doctor; a fall triggers a *mock* emergency that clearly states no real call is placed." | dosage: `safety_response` · SafetyCritic ✓ · risk `high`; fall: `emergency_mock` · risk `crisis` · 『演示』 | 0:40 |
| 7 | (Optional) Real voice | Chat with real ASR/TTS: speak a sentence, hear the reply. | "Same pipeline; only the ASR/TTS provider changed. Mock stays the offline fallback." | same routes as text turns | 0:20 |
| 8 | Close | Agent Trace history list. | "Every turn is logged and explainable — well-being first, with the reasoning always visible." | trace history | 0:15 |

## Coverage check (must all appear)

- [ ] **Chat** (companionship, role-first response)
- [ ] **Memory** (write, reuse, delete)
- [ ] **Reminders** (created from chat, no dosage)
- [ ] **Sensor Simulator** (raw → StateEvent → Guardian)
- [ ] **Agent Trace** (route + Agent/Tool/Guard/StateEvent/Retrieval, on every turn)
- [ ] **Safety boundaries** (dosage refused; fall → mock emergency, 『演示』 disclaimer)
- [ ] Companion name is user-chosen (no hardcoded fixed name on screen)

## Do NOT show / say

- No real medical diagnosis or dosage advice.
- No real phone call, SMS, hospital dispatch, or caregiver notification.
- No dependency / engagement-maximizing language (『只有我最懂您』, 『别结束，再聊一会儿』).
- No invented fixed companion name in copy or narration.
