# Poster Outline

Outline for the final research poster (CityU MSDS SDSC6002, Summer 2026). Fill
the bracketed placeholders. Keep the visual story on the framing the review
asked for (`docs/04`): **relationship-role first, well-being over engagement,
explainable proactive care**. Layout assumes a standard A0 portrait, three
columns.

---

## Header band
- **Title:** [User-Named AI Companion for Older Adults — a relationship-first, well-being-first, explainable design]
- Authors · supervisor · course · logos.
- One-line pitch: *a voice/text companion older adults name themselves; it
  prioritizes well-being over stickiness and shows its reasoning on every turn.*

## Column 1 — Why

1. **Problem & motivation**
   - Loneliness / daily support for older adults; risks of generic or
     engagement-maximizing companions; need for trust and explainability.
2. **Research question**
   - [How can a companion AI support older adults' well-being *without*
     fostering dependency, while staying safe and explainable?]
3. **Design principles** (the product's spine)
   - User-named companion (no fixed persona name).
   - Role-first response: emotional grounding → content → memory → one gentle
     follow-up.
   - Well-being over stickiness (no dependency language).
   - Hard safety boundaries (no diagnosis / dosage / real emergency).

## Column 2 — What & How

4. **System architecture** (diagram — the through-line of the poster)
   ```
   voice/text → InputRuleGuard → CoordinatorAgent
       ├── CompanionAgent      ├── GuardianAgent
       └── SafetyCriticAgent   └── tools/services
   → OutputRuleGuard → (TTS) → Agent Trace
   ```
   - Autonomous **agents**: Coordinator, Companion, Guardian, SafetyCritic.
   - **Tools/services**: rule guards, Memory, Reminder, InfoRetrieval, Sensor
     Adapter, ASR/TTS, LLM provider.
5. **Key mechanisms** (one mini-panel each, with a Trace screenshot)
   - **Explainable routing** — one route per turn, shown in the Agent Trace.
   - **Controlled retrieval** — online only for time-sensitive facts; emotional
     turns never retrieve.
   - **Proactive care boundary** — raw signal → `StateEvent` → Guardian; gentle,
     restrained, with cooldown / cap / quiet hours / refusal.
   - **Safety** — cheap rule guards always on; SafetyCritic only on risk;
     dosage/fall handled by safe templates and a *mock* emergency.
6. **Implementation**
   - FastAPI + Pydantic backend; Next.js + TypeScript frontend.
   - `DEMO_MODE` runs fully offline (fake/mock providers); real LLM + xiaomimimo
     ASR/TTS behind the same interfaces, mock fallback preserved.

## Column 3 — Does it work, and what's next

7. **Evaluation**
   - Six demo scenarios (`docs/demo_script.md`) exercised end-to-end.
   - Automated suite: [N] backend tests incl. a demo-acceptance / safety
     regression suite; all offline (no real LLM/ASR/TTS/web).
   - [Optional: qualitative walkthrough / heuristic eval notes —
     `docs/evaluation_plan.md`.]
8. **Safety & ethics**
   - No diagnosis, dosage, real emergency call, or real caregiver notification.
   - Memory is user-visible and deletable; companion name is user-chosen.
9. **Limitations**
   - Mock sensors / single-user demo; not a medical or emergency system;
     provider rate limits; mock retrieval data.
10. **Future work**
    - P1: voice experience enhancement, proactive preferences / quiet-hours /
      topic library, caregiver mock dashboard, evaluation export.
    - Real wearables behind the `SensorAdapter`; multi-user; richer evaluation.
- **Footer:** repo / contact / QR to the demo video.

---

### Visual assets to capture
- Architecture diagram (from the block above).
- Chat + **Agent Trace** screenshot (a `safety_response` turn reads best — it
  shows route, risk, SafetyCritic, and the guard steps at a glance).
- Sensor Simulator → Guardian decision screenshot.
