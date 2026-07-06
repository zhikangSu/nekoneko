# Final Report — Skeleton

Fillable structure for the final report (CityU MSDS SDSC6002, Summer 2026).
Replace every `[…]` with content; each section lists what to cover. Keep the
narrative on the **relationship-aware** main line built on three core
mechanisms: **关系编排 (relationship orchestration)**, **社会线索引入话题
(agent-agent conversational cueing)**, and **多智能体角色交互 (multi-agent
role interaction)**. The contribution is this *orchestration design* — a
relationship-role taxonomy plus rules for who speaks, who stays silent, who
follows up, who summarizes, and when to stop — not a feature count. Well-being
over engagement, explainability, and safety boundaries remain constraints, not
the headline. Long-term memory / trust / reminders / weather / sensor / voice
are **supporting mechanisms and technical foundation**, never the main
contribution.

> Source material to draw from: `docs/00_overview`, `docs/01_prd`,
> `docs/02_technical_roadmap`, `docs/03`/`docs/04` reviews, `docs/safety_policy.md`,
> `docs/evaluation_plan.md`, `docs/demo_script.md`, and this repo's code/tests.

---

## Abstract
- [150–250 words: problem, design stance, system, what was built/evaluated, key takeaway.]

## 1. Introduction
- 1.1 Motivation — reminiscence and self-expression for older adults; why *relationship roles* (rather than one generic assistant) help older adults enter and sustain memory talk.
- 1.2 The gap — generic assistants and engagement-maximizing companions; a single voice is easy to ignore or feels like interrogation. How a lightweight multi-person scene, orchestrated across relationship roles, can lower the pressure to start talking. Trust and explainability for older users.
- 1.3 **Main research question** —
  > 老年回忆陪伴中，系统如何基于话题、人生经历、关系偏好和边界需求，动态编排不同 AI 关系角色，并通过多智能体短对话作为社会线索，更自然地引导老人进入回忆与自我表达？
- 1.4 **Sub-questions** (three, mapped one-to-one to the core mechanisms):
  - **RQ1 关系编排 (relationship orchestration)** — 不同话题下哪些关系角色更适合出现？系统如何决定谁说话、谁沉默、谁总结、何时停止？
  - **RQ2 社会线索引入话题 (social cueing)** — agent-agent short cue 是否比直接提问更自然、更低压力、更容易启动回忆？
  - **RQ3 多智能体角色交互 (multi-agent role interaction)** — 同龄共鸣、晚辈好奇、中年传承、回忆整理、边界守护等角色如何协作，才能避免噪声（吵）、失真（假）、过载（乱）和越界？
- 1.5 Contributions —
  - a **relationship-role taxonomy** (关系角色分类: 同龄共鸣 / 晚辈好奇 / 中年传承 / 回忆整理 / 边界守护);
  - **dynamic relationship orchestration** (动态关系编排: who speaks / stays silent / follows up / summarizes / when to stop, driven by topic, life experience, preference, and boundary);
  - **agent-agent conversational cueing as a social memory cue** (社会线索引入话题: 2–3 roles hold a brief exchange around a photo / old object / life topic, then invite the elder in);
  - **role interaction rules** (共鸣 / 追问 / 总结 / 沉默 / 边界守护) to avoid noise, inauthenticity, overload, and boundary violation;
  - a **role / topic / boundary trace** that makes the orchestration explainable.
  - Supporting (not headline): the runnable demo backbone, the safety boundary model, and long-term memory as a familiarity/trust *dimension*.
- 1.6 Scope — a course-level demo / HCI prototype and *technical foundation*; the relationship-aware orchestration layer is the next stage (relationship-aware prototype / Wizard-of-Oz / semi-automatic). Not a medical, emergency, or production system; no completed elderly experiments claimed.

## 2. Background & related work
- Reminiscence & life-review for older adults; social cues and multi-party conversation for lowering entry pressure; relationship roles vs. a single assistant voice; companion / social agents; conversational well-being; multi-agent orchestration; LLM safety; explainable AI / agent traces. [cite]

## 3. Core mechanisms (the research stance)
The three mechanisms below are the contribution; the constraints in 3.4–3.8 shape how they are applied.
- 3.1 **Relationship-role taxonomy** — 同龄共鸣 / 晚辈好奇 / 中年传承 / 回忆整理 / 边界守护: what each role is for, its voice, and when it is appropriate.
- 3.2 **Relationship orchestration (关系编排)** — based on topic, life experience, relationship preference, and boundary need, decide who speaks, who stays silent, who follows up, who summarizes, and when to stop.
- 3.3 **Social cueing (社会线索引入话题)** — 2–3 roles hold a brief agent-agent exchange around a photo / old object / life topic, forming a lightweight multi-person scene, then invite the elder to join — instead of asking the elder a cold direct question.
- 3.4 Role-first response — emotional grounding → content → optional memory → one gentle follow-up.
- 3.5 Well-being over stickiness — explicitly avoid dependency / engagement-maximizing language.
- 3.6 User-named companion — no fixed persona name; neutral fallback 『陪伴 AI / AI Companion』; never role-play the deceased.
- 3.7 Explainability — one route per turn plus the role/topic/boundary decisions, surfaced in an Agent Trace.
- 3.8 Safety & boundary — no diagnosis, no dosage, no real emergency/caregiver action; when topics touch the deceased / grief / privacy / dependency, the system pauses, redirects, or declines (see §9).

## 4. System design
- 4.1 Overview — `voice/text → InputRuleGuard → CoordinatorAgent → {CompanionAgent | GuardianAgent | SafetyCriticAgent | tools} → OutputRuleGuard → (TTS) → Agent Trace`. Note where the **relationship-orchestration layer** sits (planned): between the Coordinator and the role-playing companion voices; current code is the technical foundation for it.
- 4.2 **Relationship orchestration & roles** (RQ1/RQ3, the core design) — the relationship-role taxonomy (同龄共鸣 / 晚辈好奇 / 中年传承 / 回忆整理 / 边界守护); how topic, life experience, preference, and boundary select which roles appear; the interaction rules (共鸣 / 追问 / 总结 / 沉默 / 边界守护); the stop/handoff logic (who summarizes, when to stop). [Note current vs. planned: single CompanionAgent today; multi-role orchestration is the next-stage prototype / Wizard-of-Oz layer.]
- 4.3 **Social cueing (agent-agent short dialogue)** (RQ2) — how 2–3 roles hold a brief exchange around a photo / old object / life topic to form a low-pressure entry, then invite the elder in; the cue-vs-direct-question contrast to be evaluated.
- 4.4 Agents vs. tools — autonomous agents (Coordinator, Companion, Guardian, SafetyCritic) vs. tools/services (rule guards, Memory, Reminder, InfoRetrieval, SensorAdapter, ASR/TTS, LLM provider). Why this split aids explainability and safety.
- 4.5 Coordinator routing — the per-turn routes (`companion_chat`, `reminder_management`, `retrieval_supported_response`, `proactive_checkin`, `safety_response`, `emergency_mock`) and how the route is chosen.
The remaining subsections are the **supporting technical foundation** (not the headline contribution):
- 4.6 Controlled retrieval — gating so emotional/reminiscence turns never hit external retrieval; only time-sensitive facts (weather/air) do.
- 4.7 Proactive care — `RawSignal → SensorAdapter → StateEvent → GuardianAgent`; restraint via cooldown, daily cap, quiet hours, refusal pause; `safety_escalation` is never silenced.
- 4.8 Memory & reminders (supporting) — markdown-first memory (user-visible, deletable) as a **familiarity/trust dimension** that feeds orchestration (recalling a topic a role can reopen), *not* a standalone contribution; reminder parsing; medication wording stays at 『按医嘱』.
- 4.9 Safety model — always-on cheap rule guards; SafetyCritic only on risk; templates; mock emergency with an explicit demo disclaimer.
- 4.10 Voice I/O (supporting) — provider interface with offline mocks (`DEMO_MODE`) and a real xiaomimimo ASR/TTS provider via `/chat/completions`, with graceful degrade to text.
- 4.11 Explainability — the AgentTrace schema (Agent / Tool / Guard / StateEvent / Retrieval) extended with a **role / topic / boundary trace**, and the Trace Panel.

## 5. Implementation
- Stack: FastAPI + Pydantic v2; Next.js 14 + TypeScript + Tailwind. Stores: JSON + markdown under `data/`.
- `DEMO_MODE` = fully offline: companion replies and retrieval use **fake/mock** providers (the demo's chat intelligence is deterministic, not a live LLM). Real **xiaomimimo ASR/TTS** is implemented behind the voice provider interface (opt-in via `DEMO_MODE=false`, mock fallback kept); a real **LLM** and **retrieval** provider remain future work behind the same provider-interface seam. [repo layout, key modules.]

## 6. Evaluation
- 6.1 Method — two layers. (a) **System/foundation checks (done):** the six demo scenarios (`docs/demo_script.md`) run end-to-end; automated demo-acceptance + safety regression suite ([N] tests, all offline). (b) **Mechanism evaluation (planned / next stage):** how RQ1–RQ3 would be assessed — orchestration appropriateness (does the right role speak/stay silent/summarize/stop for a topic), social-cueing vs. direct-question (naturalness, entry pressure, ease of starting reminiscence), and role-interaction quality (avoiding 吵 / 假 / 乱 / 越界). Reminiscence depth, self-expression, and familiarity/trust are *dimensions* here, not the headline claim. [Method sketch per `docs/evaluation_plan.md`; no completed elderly experiments claimed.]
- 6.2 Results — [what passed on the foundation: trace evidence per scenario; safety cases held; retrieval gating held; naming fallback held. Mechanism results are future work.]
- 6.3 Explainability evidence — [Trace Panel screenshots tying each scenario to its route; and, for the planned layer, the role / topic / boundary decisions the orchestration would surface.]

## 7. Discussion
- What the orchestration stance buys (natural low-pressure entry into reminiscence via social cues; the right role at the right time instead of one interrogating voice; explainable role/topic/boundary decisions).
- Trade-offs — orchestration richness vs. noise (吵) / inauthenticity (假) / overload (乱); social cueing vs. transparency; restraint vs. helpfulness; mock providers vs. real; where the LLM is and isn't trusted.
- What the current code demonstrates (foundation) vs. what the next-stage relationship-aware prototype must add.

## 8. Limitations
- Companion replies are **template-based** (FakeLLMProvider), not LLM-generated; retrieval data is mock — so language quality and factual retrieval are not representative of a real-provider deployment.
- Mock sensors and single-user demo; not medical/emergency; provider rate limits; ASR/TTS quality not formally evaluated.

## 9. Ethics & safety (incl. the boundary question)
- **Boundary discussion (not a 4th RQ, an ethics dimension)** — when topics touch the **deceased / grief / privacy / dependency**, how the system pauses, redirects, or declines; the 边界守护 role's job; never role-play the deceased; how social cueing must not manufacture false intimacy or pressure.
- Boundaries enforced (no diagnosis/dosage/real emergency/caregiver action); well-being over stickiness; memory privacy and user control; honest demo disclaimers.

## 10. Future work
- Next stage (the actual research contribution): the relationship-aware orchestration prototype — role taxonomy in code, dynamic orchestration policy, agent-agent social-cueing generation, and the role/topic/boundary trace; a Wizard-of-Oz / semi-automatic layer for elder-facing evaluation.
- Supporting P1: voice enhancement, proactive preferences / quiet-hours / topic library, caregiver mock dashboard, evaluation export. Beyond: real LLM + retrieval provider behind the existing seam, real wearables behind `SensorAdapter`, multi-user, longitudinal evaluation.

## 11. Conclusion
- [Restate the three-mechanism main line — relationship orchestration, social cueing, multi-agent role interaction — and what the current prototype (foundation) demonstrates vs. what the next stage adds.]

## References
- [...]

## Appendix
- A. Demo script (`docs/demo_script.md`) · B. Safety policy (`docs/safety_policy.md`) · C. Evaluation plan (`docs/evaluation_plan.md`) · D. Architecture & API (`docs/02_technical_roadmap`, `backend/README.md`).
