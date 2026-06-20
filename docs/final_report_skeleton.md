# Final Report — Skeleton

Fillable structure for the final report (CityU MSDS SDSC6002, Summer 2026).
Replace every `[…]` with content; each section lists what to cover. Keep the
narrative on the framing the review asked for (`docs/04`): **relationship-role
first, well-being over engagement, explainable proactive care** — the
contribution is the *design stance*, not a feature count.

> Source material to draw from: `docs/00_overview`, `docs/01_prd`,
> `docs/02_technical_roadmap`, `docs/03`/`docs/04` reviews, `docs/safety_policy.md`,
> `docs/evaluation_plan.md`, `docs/demo_script.md`, and this repo's code/tests.

---

## Abstract
- [150–250 words: problem, design stance, system, what was built/evaluated, key takeaway.]

## 1. Introduction
- 1.1 Motivation — loneliness and daily support for older adults; why a *relationship-first* companion.
- 1.2 The gap — generic assistants and engagement-maximizing companions; trust and explainability for older users.
- 1.3 **Research question(s)** — [e.g. *How can a companion AI support older adults' well-being without fostering dependency, while remaining safe and explainable?*]
- 1.4 Contributions — [the design principles + the explainable multi-agent architecture + the runnable demo + the safety boundary model.]
- 1.5 Scope — a course-level demo / HCI prototype; not a medical, emergency, or production system.

## 2. Background & related work
- Companion / social agents for older adults; conversational well-being; LLM safety; explainable AI / agent traces. [cite]

## 3. Design principles (the product stance)
- 3.1 User-named companion — no fixed persona name; neutral fallback 『陪伴 AI / AI Companion』.
- 3.2 Role-first response — emotional grounding → content → optional memory → one gentle follow-up.
- 3.3 Well-being over stickiness — explicitly avoid dependency / engagement-maximizing language.
- 3.4 Explainability — one route per turn, surfaced in an Agent Trace.
- 3.5 Safety boundaries — no diagnosis, no dosage, no real emergency/caregiver action.

## 4. System design
- 4.1 Overview — `voice/text → InputRuleGuard → CoordinatorAgent → {CompanionAgent | GuardianAgent | SafetyCriticAgent | tools} → OutputRuleGuard → (TTS) → Agent Trace`.
- 4.2 Agents vs. tools — autonomous agents (Coordinator, Companion, Guardian, SafetyCritic) vs. tools/services (rule guards, Memory, Reminder, InfoRetrieval, SensorAdapter, ASR/TTS, LLM provider). Why this split aids explainability and safety.
- 4.3 Coordinator routing — the per-turn routes (`companion_chat`, `reminder_management`, `retrieval_supported_response`, `proactive_checkin`, `safety_response`, `emergency_mock`) and how the route is chosen.
- 4.4 Controlled retrieval — gating so emotional/reminiscence turns never hit external retrieval; only time-sensitive facts (weather/air) do.
- 4.5 Proactive care — `RawSignal → SensorAdapter → StateEvent → GuardianAgent`; restraint via cooldown, daily cap, quiet hours, refusal pause; `safety_escalation` is never silenced.
- 4.6 Memory & reminders — markdown-first memory (user-visible, deletable); reminder parsing; medication wording stays at 『按医嘱』.
- 4.7 Safety model — always-on cheap rule guards; SafetyCritic only on risk; templates; mock emergency with an explicit demo disclaimer.
- 4.8 Voice I/O — provider interface with offline mocks (`DEMO_MODE`) and a real xiaomimimo ASR/TTS provider via `/chat/completions`, with graceful degrade to text.
- 4.9 Explainability — the AgentTrace schema (Agent / Tool / Guard / StateEvent / Retrieval) and the Trace Panel.

## 5. Implementation
- Stack: FastAPI + Pydantic v2; Next.js 14 + TypeScript + Tailwind. Stores: JSON + markdown under `data/`.
- `DEMO_MODE` = fully offline (fake/mock providers); real providers behind the same interfaces. [repo layout, key modules.]

## 6. Evaluation
- 6.1 Method — the six demo scenarios (`docs/demo_script.md`) run end-to-end; automated demo-acceptance + safety regression suite ([N] tests, all offline). [Optional: heuristic/qualitative walkthrough per `docs/evaluation_plan.md`.]
- 6.2 Results — [what passed; trace evidence per scenario; safety cases held; retrieval gating held; naming fallback held.]
- 6.3 Explainability evidence — [Trace Panel screenshots tying each scenario to its route + steps.]

## 7. Discussion
- What the design stance buys (trust, restraint, explainability); trade-offs (mock providers, restraint vs. helpfulness); where the LLM is and isn't trusted.

## 8. Limitations
- Mock sensors and single-user demo; not medical/emergency; provider rate limits; mock retrieval data; ASR/TTS quality not formally evaluated.

## 9. Ethics & safety
- Boundaries enforced (no diagnosis/dosage/real emergency/caregiver action); well-being-first; memory privacy and user control; honest demo disclaimers.

## 10. Future work
- P1: voice enhancement, proactive preferences / quiet-hours / topic library, caregiver mock dashboard, evaluation export. Beyond: real wearables behind `SensorAdapter`, multi-user, longitudinal evaluation.

## 11. Conclusion
- [Restate the stance and what the prototype demonstrates.]

## References
- [...]

## Appendix
- A. Demo script (`docs/demo_script.md`) · B. Safety policy (`docs/safety_policy.md`) · C. Evaluation plan (`docs/evaluation_plan.md`) · D. Architecture & API (`docs/02_technical_roadmap`, `backend/README.md`).
