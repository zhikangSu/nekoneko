# Poster Outline

Outline for the final research poster (CityU MSDS SDSC6002, Summer 2026). Fill
the bracketed placeholders. The visual story is the **relationship-aware
orchestration** main line: for elderly reminiscence companionship, how the
system *dynamically orchestrates different AI relationship roles* — deciding who
speaks, who stays silent, who follows up, who summarizes, and when to stop — and
uses **short agent-agent dialogue as a social cue** to invite the elder into
recollection and self-expression. Well-being over engagement and safe boundaries
run through the whole story. Layout assumes a standard A0 portrait, three
columns.

The poster does **not** present a feature list as its contribution. Reminder /
weather / sensor / voice are supporting capabilities; long-term memory is a
supporting / boundary mechanism — none of these is the main line.

---

## Header band
- **Title:** [Relationship-Aware Orchestration for Elderly Reminiscence — dynamically arranging AI relationship roles, using multi-agent social cues to invite recollection]
- Authors · supervisor · course · logos.
- One-line pitch: *for older adults, 2–3 AI relationship roles hold a short,
  low-pressure chat around a photo or old object, then gently invite the elder
  in — the system decides who speaks, who stays silent, who follows up, and when
  to stop.*

## Column 1 — Why & the research question

1. **Problem & motivation**
   - Reminiscence supports older adults' well-being, but a single companion
     asking direct questions can feel like an interview — high-pressure and easy
     to stall. Generic or engagement-maximizing companions add noise, feel
     inauthentic, overload, or cross boundaries. Recollection needs a natural
     social scene, restraint, and explainability.
2. **Main research question**
   - *在老年回忆陪伴中，系统如何基于话题、人生经历、关系偏好和边界需求，动态编排不同 AI 关系角色，*
     *并通过多智能体短对话作为社会线索，更自然地引导老人进入回忆与自我表达？*
3. **Three sub-questions** (mapped to the three core mechanisms)
   - **RQ1 关系编排 (relationship orchestration):** 不同话题下哪些关系角色更适合出现？
     系统如何决定谁说话、谁沉默、谁总结、何时停止？
   - **RQ2 社会线索引入话题 (social cueing):** agent-agent short cue 是否比直接提问更自然、
     更低压力、更容易启动回忆？
   - **RQ3 多智能体角色交互 (role interaction):** 同龄共鸣、晚辈好奇、中年传承、回忆整理、
     边界守护等角色如何协作，才能避免噪声(吵)、失真(假)、过载(乱)和越界？
4. **Design principles** (the spine underneath the main line)
   - Well-being over stickiness (no dependency language).
   - User-named companion (no fixed persona name); neutral fallback 陪伴 AI /
     AI Companion.
   - Hard safety / boundary rules (no diagnosis / dosage / real emergency; never
     role-play the deceased).

## Column 2 — The main line: relationship-aware orchestration

4. **Core contributions** (the poster's headline — not a feature list)
   - **Relationship-role taxonomy (关系角色分类):** 同龄共鸣 / 晚辈好奇 / 中年传承 /
     回忆整理 / 边界守护 — a small set of relationship roles, not generic "agents".
   - **Dynamic relationship orchestration (动态关系编排):** based on topic, life
     experience, relationship preference and boundary needs, decide *who speaks,
     who stays silent, who follows up, who summarizes, and when to stop*.
   - **Agent-agent conversational cueing (社会线索引入话题):** 2–3 roles hold a brief
     chat around a photo / old object / life topic, forming a lightweight
     multi-person scene, then invite the elder to join — a social memory cue
     instead of a direct question.
   - **Role interaction rules:** 共鸣 / 追问 / 总结 / 沉默 / 边界守护, tuned to avoid
     noise (吵), inauthenticity (假), overload (乱), and boundary violations.
   - **Role / topic / boundary trace:** every turn shows which roles were
     arranged, why, and where the system paused or declined.
5. **System architecture** (diagram — the orchestration backbone)
   ```
   voice/text → InputRuleGuard → CoordinatorAgent (relationship orchestration)
       ├── relationship roles: 同龄共鸣 / 晚辈好奇 / 中年传承 / 回忆整理 / 边界守护
       ├── GuardianAgent      ├── SafetyCriticAgent
       └── supporting tools/services
   → OutputRuleGuard → (TTS) → Role / Topic / Boundary Trace
   ```
   - **Coordinator** orchestrates which relationship roles speak, follow up,
     summarize, or stay silent per turn; **Guardian** and **SafetyCritic** hold
     the boundary.
   - Relationship roles are realized on top of the companion layer; **boundary
     守护** is the role that pauses, redirects, or declines.
6. **Supporting capabilities & technical foundation** (enable the main line, not the contribution)
   - Rule guards, **long-term memory** (a supporting / boundary mechanism — helps
     continuity and personalization, *not* a standalone research claim), Reminder,
     InfoRetrieval, Sensor Adapter, ASR/TTS, LLM provider.
   - **Proactive care boundary** — raw signal → `StateEvent` → Guardian; gentle,
     restrained, with cooldown / cap / quiet hours / refusal.
   - **Controlled retrieval** — online only for time-sensitive facts; emotional /
     reminiscence turns never retrieve.
   - **Safety** — cheap rule guards always on; SafetyCritic only on risk;
     dosage/fall handled by safe templates and a *mock* emergency.
7. **Implementation & honest scope**
   - FastAPI + Pydantic backend; Next.js + TypeScript frontend. Current code is
     the **technical foundation / demo backbone**, not the whole research: the
     next stage adds the relationship-aware prototype (Wizard-of-Oz /
     semi-automatic orchestration layer).
   - `DEMO_MODE` runs fully offline — companion replies and retrieval use
     **fake/mock providers** (deterministic, not a live LLM). Real **xiaomimimo
     ASR/TTS** is optional behind the voice provider interface (opt-in via
     `DEMO_MODE=false`, mock fallback kept). A real **LLM** and a real
     **retrieval** provider are provider-interface / future work behind the same
     seam — *not* claimed as done.

## Column 3 — Evaluation, boundary ethics, and what's next

8. **Evaluation** (organized by the three sub-questions)
   - **RQ1 orchestration:** does role arrangement (who speaks / stays silent /
     summarizes / stops) fit the topic and preference? — role/topic trace review.
   - **RQ2 social cueing:** is an agent-agent short cue more natural, lower
     pressure, and easier to start recollection than a direct question? —
     side-by-side walkthroughs.
   - **RQ3 role interaction:** do 共鸣 / 追问 / 总结 / 沉默 / 边界守护 cooperate without
     noise, inauthenticity, overload, or boundary violation?
   - Demo scenarios (`docs/demo_script.md`) exercised end-to-end; automated
     suite: [N] backend tests incl. safety regression; all offline (no real
     LLM/ASR/TTS/web). *No real elderly experiments completed yet* — planned for
     the next prototype stage. [`docs/evaluation_plan.md`.]
9. **Boundary as ethics** (a discussion, not a fourth parallel RQ)
   - When topics touch the deceased / grief / privacy / dependency, the
     边界守护 role and guards **pause, redirect, or decline** — the system never
     role-plays the deceased, never diagnoses, never gives dosage, never places a
     real emergency call or caregiver notification.
   - Memory is user-visible and deletable; the companion name is user-chosen.
10. **Limitations**
    - Current build is a demo backbone; orchestration/cueing prototype is next.
      Mock sensors / single-user demo; not a medical or emergency system; mock
      retrieval; provider rate limits.
11. **Future work**
    - Relationship-aware prototype: fuller **dynamic orchestration** + agent-agent
      **social cueing**, evaluated in a Wizard-of-Oz / semi-automatic study.
    - Real **LLM** and **retrieval** providers behind the existing provider
      interfaces (so role replies are model-generated, not template-based).
    - Supporting P1: voice enhancement, proactive preferences / quiet-hours /
      topic library, caregiver mock dashboard; real wearables behind the
      `SensorAdapter`; multi-user; richer evaluation.
- **Footer:** repo / contact / QR to the demo video.

---

### Visual assets to capture
- Architecture diagram (the orchestration backbone from the block above).
- **Role / Topic / Boundary Trace** screenshot showing which relationship roles
  were arranged, who followed up / summarized / stayed silent, and where the
  system paused (reads best as the poster's centerpiece).
- Agent-agent **social cue** mock — 2–3 roles chatting around a photo, then
  inviting the elder in.
- Sensor Simulator → Guardian decision screenshot (supporting mechanism).
