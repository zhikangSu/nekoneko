# Evaluation Plan (Draft)

Status: draft / entry point (Slice 1). The full HCI evaluation design — task
list, SUS/Likert instruments, and interview guide — is tracked in issue #15 and
will expand this file. Canonical positioning lives in
`docs/01_prd_elderly_multi_agent_companion_ai.md`.

---

## 1. What this evaluation is (and is not)

The MVP evaluates **interaction feasibility, trust, perceived companionship,
willingness to continue use, and perceived appropriateness of proactive care**.

It does **not** evaluate clinical effectiveness, medical outcomes, or real-world
health impact. There is no diagnosis, no treatment, and no real participant
health data in the demo.

Participants may be role-play or convenience participants. Recruiting real older
adults requires ethics / informed-consent handling per supervisor guidance
(`docs/00_overview` 目标用户范围).

---

## 2. Research focus

```text
Can older users complete core tasks (chat, reminder, memory, retrieval)?
Do users trust the system's boundaries (safety, privacy, control)?
Do users perceive companionship without manipulation or dependency?
Would users be willing to come back and keep using it?
Is proactive care perceived as caring rather than intrusive?
```

---

## 3. Candidate measures (to be finalized in #15)

| Dimension | Candidate measure |
|---|---|
| Usability | SUS (System Usability Scale) |
| Perceived companionship | Likert items (warmth, being heard, being remembered) |
| Trust & safety | Likert items (boundary clarity, privacy control) |
| Continuance intention | Likert items (willingness to return / keep using) |
| Proactive-care appropriateness | Likert items (helpful vs. intrusive) |
| Qualitative | Semi-structured interview, think-aloud notes |

A planned study condition compares **trace-visible vs. trace-hidden** to test how
transparency affects trust (P1, see `AGENTS.md` §6).

---

## 4. Task scenarios

Evaluation tasks mirror the six demo capabilities in
[demo_script.md](demo_script.md): companionship, reminder, memory, proactive
care, controlled retrieval, and safety boundary. Each task gets a short success
definition and observation notes.

---

## 5. Data handling

```text
no real medical or identifying participant data in the demo
evaluation responses stored locally (see evaluation_sessions / evaluation_responses)
export is for analysis only; covered by issue #20 (P1)
no real recordings committed to the repo
```

---

## 6. Next steps (issue #15)

```text
finalize task list with success criteria
finalize SUS + Likert instrument wording (zh / en)
write the semi-structured interview guide
define scoring and a lightweight analysis plan
```
