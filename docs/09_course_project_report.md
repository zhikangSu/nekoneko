# Relationship-Aware Multi-Agent Reminiscence Companion for Older Adults

**Project Report — English Submission Version**

**Course:** City University of Hong Kong, MSDS, SDSC6002 Research Project, Summer 2026<br>
**Project stage:** Completed course-level software prototype<br>
**Version date:** 21 July 2026<br>
**Project lead / student ID:** Xiaoya Fei59384046
**Other team members / student IDs:** Zhikang Su59844749、Ziyi Zhao59892747、Boxuan An59735190

> Return willingly, use safely. Companionship first, retrieval when needed, safety always.

## Abstract

This project develops a relationship-aware, multi-agent reminiscence companion for older adults. It addresses a practical interaction problem: a conventional chatbot’s direct question can feel like an interview, while an unconstrained multi-character conversation can become noisy, artificial, or unsafe. The system therefore treats **relationship orchestration** as its core mechanism. It decides which non-autonomous relationship roles should speak, remain silent, follow up, summarize, or stop, while four autonomous agents coordinate dialogue, companionship, proactive care, and risk review.

A user-named companion, transparent memory controls, restrained proactive check-ins, controlled retrieval, and a per-turn Agent Trace support trust and system observability. The implemented prototype uses a Next.js frontend and FastAPI backend, supports configurable real and mock language, voice, and weather providers, and remains runnable offline in demo mode. At the verified implementation snapshot, 382 backend tests pass and the frontend production build succeeds.

This report documents the completed school project as an implemented software system. It focuses on requirements, architecture, modules, interaction design, safety controls, implementation choices, and engineering verification. The cited CHI and multi-agent literature is used to justify design decisions rather than to present an experimental study conducted by this project.

**Keywords:** older adults; reminiscence; conversational AI; multi-agent systems; relationship orchestration; social cueing; human–AI interaction; safety

> **Project boundary:** The completed deliverable is a runnable course-level software prototype. It does not claim clinical effects, real emergency response, or production deployment readiness.

## 1. Introduction

### 1.1 Motivation and problem

Reminiscence can help people articulate identity, relationships, and life experience, and it has long been discussed as a meaningful activity in later life [1]. Digital conversational systems can lower the practical barrier to starting such conversations, yet many systems still follow an assistant-first pattern: ask a question, wait for an answer, and optimize for task completion.

For older adults, this pattern can create entry pressure, particularly when prompts concern family, bereavement, health, or private memories. At the other extreme, several simulated characters speaking freely may increase social presence but can also create interruption, repetition, false intimacy, and boundary violations. The design challenge is therefore not simply to add more agents. It is to organize a small and legible social setting that helps the user enter a topic while preserving control.

### 1.2 Project objectives

The project aims to deliver a complete local prototype that can support low-pressure reminiscence, distinguish autonomous agents from visible relationship roles, preserve user control over memory and proactive care, expose system decisions through Agent Trace, and keep safety boundaries active across text, voice, retrieval, and simulated sensor flows.

### 1.3 Completed outcomes

- A usable Next.js interface for onboarding, chat, memory, reminders, sensors, caregiver mock views, and trace inspection.
- A FastAPI backend implementing guarded routing, four autonomous agents, relationship-role orchestration, memory authorization, reminders, retrieval, and provider abstractions.
- Configurable real and mock LLM, ASR, TTS, and weather services, with offline demo support and visible fallback metadata.
- A verified build with 382 passing backend tests and a successful frontend production build.

### 1.4 Contributions

The project contributes:

1. A relationship-orchestration model that separates autonomous agents from visible social roles.
2. A deterministic and traceable policy for selecting the smallest useful speaker set.
3. A runnable full-stack prototype with memory, reminders, sensor-derived care, controlled retrieval, voice, and layered safety.
4. A stable Agent Trace and engineering-verification layer that makes multi-agent behavior inspectable and testable.

### 1.5 Scope

This is a completed course-level software prototype designed for a broad older-adult population. It does not diagnose illness, recommend treatment or medication changes, detect falls, contact emergency services, notify caregivers, or claim therapeutic outcomes. The delivered scope is a local, demonstrable, traceable, and safety-bounded companion system.

## 2. Background and Related Work

### 2.1 Reminiscence and later-life interaction

Butler framed life review as a naturally occurring process in later life rather than a pathology [1]. Meta-analytic and systematic-review evidence suggests that structured reminiscence interventions can have beneficial psychosocial effects in some settings, but results vary by population, method, and outcome [2, 3]. This project therefore uses reminiscence as an interaction domain, not as a clinical treatment. It evaluates whether the interface helps users speak comfortably and meaningfully, not whether it treats depression, dementia, or loneliness.

### 2.2 Multi-agent reminiscence and role-based interaction

Long-term relational-agent research indicates that social-relational behaviors can influence trust, liking, and continued engagement [4]. A 2025 systematic review of conversational AI for aging found recurring needs for natural communication, personalization, user control, privacy, accessibility, and dependable response quality [5].

ReminiBuddy is the closest domain reference to this project. It combines older and younger responding agents with personal photographs and generic nostalgic objects, showing that agent identity and memory-cue type can support different forms of reminiscence [10]. Cinema Multiverse Lounge similarly demonstrates how several visible personas can contribute complementary viewpoints in a shared conversational experience [17]. These systems support the use of differentiated roles, but they also motivate this project’s additional focus on turn control, stopping, safety, and explicit orchestration.

### 2.3 Human control and restrained orchestration

Human–AI interaction guidance emphasizes setting expectations, enabling correction, supporting efficient dismissal, and making system behavior understandable [6]. Trust should support appropriate reliance rather than maximum reliance [7]. Collaborative remembering can provide retrieval cues but can also suppress or contaminate recall [8, 9].

Recent multi-agent interface work further shows that users benefit when they can select, steer, and reorganize AI contributors rather than passively receive an autonomous group conversation. Perspectra emphasizes user-selected experts and structured deliberation [12]; CrafTeam shows a shift toward human-orchestrated agent teams [14]; MultiColleagues uses differentiated professional roles and facilitation for structured ideation [16]; and YES AND proposes confidence-based turn-taking so only relevant agents contribute [19]. These ideas inform the project’s manual role controls, smallest-useful-speaker policy, and explicit ability to disable relationship roles.

### 2.4 Observability, transparency, and debugging

Multi-agent systems require more than role prompts. They need a clear operational record of routing, messages, tools, and state changes. AGDebugger supports message-level inspection, reset, editing, and branch comparison [11], while DiLLS organizes agent behavior into layered activity, action, and operation summaries [15]. Industry accounts similarly identify complexity management, transparency, and the balance between autonomy and human oversight as practical design priorities [18].

Transparency must also be calibrated. Sensemaking research on multi-agent LLM interfaces shows that agent agreement, disagreement, critique, and visible process details can either support or undermine trust depending on presentation and cognitive load [13]. The present project therefore uses progressive Agent Trace: the user-facing response remains simple, while detailed routing, role, guard, retrieval, memory, and provider information is available for demonstration and diagnosis.

## 3. Design Principles and Core Mechanisms

### 3.1 Overall Design Objective

The product principle is: **return willingly, use safely; companionship first, retrieval when needed, safety always**. The system is relationship-first rather than assistant-first, but it must not simulate exclusivity, dependency, or a real family member. The companion display name is chosen by the user. Before naming, the interface uses a neutral label such as “AI Companion”.

### 3.2 Relationship orchestration

Relationship orchestration is the central decision layer. For each turn, it interprets the topic, sensitivity, prior interaction state, user-selected roles, and stopping signals. It then chooses who speaks, in what order, and for what function.

The default is the smallest useful speaker set. A topic-card opening may stage two short role messages to create a social cue, while follow-up turns usually use one role. Sensitive topics suppress role banter and route to a boundary guardian or neutral companion response.

### 3.3 Social roles are not autonomous agents

The current registry contains eight visible roles. They represent conversational viewpoints and functions, not independent autonomous entities. Manual selection supports up to three roles, while `no_ai_role` is exclusive.

| Role | Interaction function | Primary boundary |
|---|---|---|
| Same-age peer | Resonates with era, routine, and shared-generation references | Must not claim a real shared past |
| Curious junior | Asks gentle, respectful questions from a younger perspective | Must not infantilize or interrogate |
| Middle-age bridge | Connects generations and explains context | Must not speak for real family members |
| Elder mentor | Invites values, advice, and life lessons | Must not pressure the user to perform wisdom |
| Theme companion | Keeps a chosen reminiscence topic coherent | Must stop when the user changes or declines the topic |
| Memory organizer | Summarizes only user-provided material for confirmation | Must not invent or silently save details |
| Boundary guardian | Pauses, redirects, or declines unsafe role-play | Takes priority at sensitive boundaries |
| No-AI-role | Disables relationship-role cueing | Exclusive manual option |

### 3.4 Agent–agent social cueing

On an eligible topic-card opening, selected roles can exchange two brief, non-factual prompts before inviting the older adult to contribute. The purpose is not to perform a theatrical conversation or fabricate a shared past. It is to model an approachable way into the topic: one role may resonate, another may ask gently, and the companion then returns the floor to the user.

The cue is deliberately short and stops immediately when the user declines, changes topic, or enters a sensitive area.

### 3.5 Interaction rules

The policy supports five functional moves: resonate, follow up, bridge generations, summarize memories, and guard boundaries. It also treats silence and stopping as first-class actions. Roles must not compete, repeat the same point, impersonate deceased people, claim private knowledge, or tell users that the AI is their only source of understanding.

External information retrieval is reserved for time-sensitive facts such as weather or opening hours. Emotional disclosure, reminiscence, memory editing, and reminder creation do not trigger web retrieval.

## 4. System Architecture and Implementation

### 4.1 Runtime architecture

The prototype is organized as a guarded state-and-routing workflow:

```text
User voice or text
  → InputRuleGuard
  → CoordinatorAgent: route and state decision
  → Relationship orchestration: roles, turn order, and boundaries
  → CompanionAgent: response draft
  → OutputRuleGuard
  → Final response + Agent Trace

Supporting paths:
  StateEvent → GuardianAgent → check-in / defer / silent log / safety escalation
  Risk or high uncertainty → SafetyCriticAgent
  Coordinator decision → Memory / Reminder / Retrieval / Voice services
```

Every chat turn returns an Agent Trace containing the turn ID, mode, route, risk level, agents, tools, guards, state event, memory use, retrieval use, safety-review use, and relationship-research fields.

### 4.2 Autonomous agents

| Autonomous agent | Responsibility | Decision output |
|---|---|---|
| CoordinatorAgent | Chooses route and maintains turn state | Route, rationale, and selected roles |
| CompanionAgent | Produces user-facing relational dialogue | Bounded response in the user-named persona |
| GuardianAgent | Decides restrained proactive care from StateEvents | `check_in`, `defer`, `silent_log`, or `safety_escalation` |
| SafetyCriticAgent | Reviews risky or highly uncertain content | Safety critique or safe response |

The design deliberately avoids calling every classifier, store, provider, or visible role an agent.

### 4.3 Tools and services

EmotionClassifierTool, MemoryStore, ReminderScheduler, InfoRetrievalTool, SensorAdapter, input/output rule guards, Voice I/O services, and provider interfaces are tools or services.

The boundary between raw signals and care decisions is explicit:

```text
RawSignal → SensorAdapter / StateEncoder → StateEvent → GuardianAgent
```

This prevents GuardianAgent from interpreting mock sensor readings as medical evidence.

### 4.4 Technology stack

The frontend uses Next.js 14, React 18, TypeScript, and Tailwind CSS. The backend uses Python 3.11+, FastAPI, Pydantic v2, and HTTPX.

The prototype currently stores structured records in JSON and human-readable memory in Markdown. SQLite remains a planned structured-storage upgrade rather than a completed dependency. Provider interfaces support fake or Xiaomi MiMo language generation, mock or Xiaomi MiMo ASR/TTS, and mock or Open-Meteo weather retrieval. Demo mode remains offline-capable, and automated tests do not call paid or external providers.

### 4.5 Memory, reminders, and user control

Memory is transparent and user-controllable. The Memory Center supports viewing, adding, deleting, and pausing memory categories. Proposed memory cards require authorization before storage. Sensitive credentials, identity numbers, financial data, unverified emotional inferences, and details the user asks the system to forget are not saved automatically.

Reminders are stored separately from autobiographical memory and support explicit create, review, and delete operations.

### 4.6 Restrained proactive care

Guardian decisions include a care proposal, restraint critique, decision, reason, cooldown status, and visible trace summary. Default policy includes:

- A two-hour same-topic cooldown.
- No more than three casual proactive check-ins per day.
- Quiet hours from 22:00 to 07:00.
- A 24-hour pause after refusal.
- Voice output off at night unless explicitly enabled.

Wording remains uncertain and observational, avoiding claims such as “you are ill” or “you must be lonely”.

## 5. Interaction Flows and Representative Scenarios

### 5.1 First-run onboarding

The user reviews the system’s non-human identity, privacy boundaries, and safety limits; chooses a companion display name; configures voice and proactive-care preferences; and may retain automatic relationship-role selection or choose roles manually. Consent and control are part of the main product flow rather than hidden in a settings appendix.

### 5.2 Reminiscence topic opening

For a non-sensitive topic such as Cantonese opera, the Coordinator selects the relationship-cueing route. A same-age peer may offer brief resonance, a curious junior may ask what first attracted the user, and the companion then invites the user to continue. Subsequent turns normally reduce to one role to preserve focus. The trace shows why the roles were selected and whether the user overrode the automatic choice.

### 5.3 Sensitive memory

If the user mentions a deceased partner, health concern, privacy-sensitive detail, or dependency cue, playful multi-role exchange is suspended. The boundary guardian or neutral companion acknowledges the feeling without impersonating the person, inventing facts, or turning the exchange into therapy.

If urgent risk terms appear, the input guard routes to a safe template and appropriate real-world support language, without claiming that emergency contact has been made.

### 5.4 Time-sensitive information

A question such as “Is the weather suitable for a walk this afternoon?” may call the controlled weather-retrieval service. The response distinguishes retrieved data from companionship content and records retrieval use in the trace. If the provider is unavailable, the prototype may use an explicit mock or fallback response. Natural-sounding wording alone is not treated as evidence that a real provider succeeded.

### 5.5 Proactive check-in

A simulated signal is normalized into a StateEvent before GuardianAgent sees it. GuardianAgent evaluates cooldown, quiet hours, daily limits, prior refusal, and uncertainty, and it can decide to remain silent. When it does check in, the wording is optional and low-pressure, for example: “It looks like today may have been a little quieter than usual. If now is convenient, I can stay and chat for a moment.”

## 6. Engineering Validation and Current Results

### 6.1 Verification scope

The completed system was verified through automated tests, production-build checks, and local runtime inspection. At the verified implementation snapshot dated 21 July 2026:

| Verification item | Status | Scope |
|---|---|---|
| Backend automated tests | 382 passed | Routing, safety, trace, roles, memory, reminders, retrieval, Guardian policy, and provider fallback |
| Frontend production build | Passed | Compilation, type checking, and lint stage |
| Offline demo mode | Supported | Fake/mock providers; no paid calls in tests |
| Trace and safety regression coverage | Passed | Required trace fields, risk routing, provider fallback, and role boundaries |

### 6.2 Demonstrated capabilities

The demonstration supports:

- First-run onboarding with a user-named companion.
- Text chat and configurable voice input/output.
- Automatic and manual relationship-role selection.
- Multi-role cue messages and visible orchestration reasons.
- A per-turn Agent Trace.
- Memory-card authorization and memory management.
- Reminder management.
- Sensor-simulator events and restrained Guardian decisions.
- Controlled weather retrieval.
- Configurable real or mock LLM, ASR, and TTS providers.
- Trace fields indicating provider fallback and conversation-history use.

### 6.3 Interpretation

Passing tests and a successful build establish implementation consistency and demo readiness within the tested environment. They do not establish production reliability, universal accessibility, clinical benefit, or readiness for real emergency use.

## 7. System Design Discussion

### 7.1 Why orchestration matters

The prototype treats multi-agent value as a coordination problem rather than a character-count problem. A role is useful only when it performs a clear conversational function at the right moment. Silence, deferral, and returning the floor to the user are therefore positive outcomes. This reframing connects system architecture to HCI goals: reduced entry pressure, clearer agency, and fewer socially awkward or unsafe exchanges.

### 7.2 Rule-based policy and explainability

The current orchestration policy is deterministic and topic-aware. This limits expressive flexibility but improves reproducibility, testability, and traceability at the prototype stage. Researchers can inspect selected roles, policy reasons, sensitivity flags, and override status. Future learning-based orchestration should be evaluated against this interpretable baseline rather than assumed superior.

### 7.3 Appropriate trust

Warmth is valuable only when paired with honest boundaries. The system identifies itself as AI, never claims to be a doctor or family member, avoids exclusivity, and encourages real-world support when appropriate. Memory authorization and visible traces help users understand what the system retained and why it behaved as it did. These mechanisms aim for appropriate trust, not maximum emotional attachment.

## 8. Ethics, Safety, Privacy, and Accessibility

### 8.1 Safety boundaries

Input and output rule guards remain active on every turn. High-risk symptoms, self-harm language, medication-dose questions, and emergency requests route to safe templates and, where needed, SafetyCriticAgent. The system does not provide diagnosis, dosage changes, treatment recommendations, or confirmation of emergency dispatch.

### 8.2 Privacy and memory

The user can inspect, correct, delete, or pause memory. Sensitive content is not silently converted into long-term memory. Research logs should be minimized, pseudonymized, access-controlled, and separated from raw voice recordings. A production deployment would require explicit retention periods, encryption, deletion workflows, and a clearer data-governance policy.

### 8.3 Accessibility and non-manipulation

The interface prioritizes large controls, readable typography, clear voice state, transcript fallback, and simple stopping actions. It avoids youth slang, coercive nudges, endless engagement loops, and statements that the AI alone understands the user. Proactive care can be refused or disabled, and refusal is respected through cooldown policy.

## 9. Limitations

The completed deliverable is a local course prototype rather than a production or clinical system. The current role taxonomy and orchestration rules remain configurable design choices. Topic classification and safety rules are language- and phrase-dependent, while real speech may contain dialects, disfluency, background noise, and ambiguous intent.

JSON and Markdown storage are suitable for a local demo but not a production-grade privacy architecture. External LLM, ASR, TTS, and weather providers can fail or behave inconsistently, and fallback behavior must remain visible. The current system also does not model long-term relationship change, caregiver workflows, clinical integration, real sensors, or emergency response. Further deployment-oriented validation would be required before use beyond the controlled course-demo setting.

## 10. Future Maintenance and Extension

Future maintenance priorities include stronger structured storage, clearer provider/fallback indicators, improved dialect and interruption handling, more robust accessibility checks, and exportable trace records for demonstrations. Later extensions may include interruption-aware voice, feedback tokens, and carefully bounded personalization. Real wearable integration, hospital integration, fall detection, emergency calling, and clinical claims remain out of scope unless separately approved and governed.

## 11. Team Contribution

The following table summarizes the final division of responsibilities among the project members.

| Member / Student ID | Responsibilities |
|---|---|
| Xiaoya Fei / 59384046 | Responsible for project conceptualization, preliminary research, requirements analysis, the design and implementation of all functional modules, and troubleshooting; took primary responsibility for drafting, organizing, and revising the project report. |
| Zhikang Su / 59844749 | Responsible for establishing the initial project framework, supporting the system architecture, functional testing, build verification, and preparation of the project poster. |
| Ziyi Zhao / 59892747 | Participated in general project communication, remained informed of project progress, and assisted with the visual refinement of the project poster. |
| Boxuan An / 59735190 | Participated in general project communication, remained informed of project progress, and assisted with the visual refinement of the project poster. |

## 12. Conclusion

This project demonstrates a relationship-aware alternative to conventional assistant-first reminiscence dialogue. Its main contribution is not the presence of multiple speaking characters, but a bounded orchestration policy that chooses a minimal useful set of social cues, preserves silence and stopping, and exposes decisions through trace data.

The full-stack prototype integrates user naming, memory control, reminders, proactive care, controlled retrieval, voice providers, and layered safety while remaining runnable in offline demo mode. Engineering verification confirms the completed system’s internal consistency and demonstration readiness within the tested environment.

## References

[1] Butler, R. N. (1963). The life review: An interpretation of reminiscence in the aged. *Psychiatry, 26*(1), 65–76. https://doi.org/10.1080/00332747.1963.11023339

[2] Pinquart, M., & Forstmeier, S. (2012). Effects of reminiscence interventions on psychosocial outcomes: A meta-analysis. *Aging & Mental Health, 16*(5), 541–558. https://doi.org/10.1080/13607863.2011.651434

[3] Woods, B., O’Philbin, L., Farrell, E. M., Spector, A. E., & Orrell, M. (2018). Reminiscence therapy for dementia. *Cochrane Database of Systematic Reviews*, 3, CD001120. https://doi.org/10.1002/14651858.CD001120.pub3

[4] Bickmore, T. W., & Picard, R. W. (2005). Establishing and maintaining long-term human–computer relationships. *ACM Transactions on Computer-Human Interaction, 12*(2), 293–327. https://doi.org/10.1145/1067860.1067867

[5] Huang, Y., Zhou, Q., & Piper, A. M. (2025). Designing conversational AI for aging: A systematic review of older adults’ perceptions and needs. *Proceedings of the CHI Conference on Human Factors in Computing Systems*. https://doi.org/10.1145/3706598.3713578

[6] Amershi, S., et al. (2019). Guidelines for human–AI interaction. *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, Paper 3, 1–13. https://doi.org/10.1145/3290605.3300233

[7] Lee, J. D., & See, K. A. (2004). Trust in automation: Designing for appropriate reliance. *Human Factors, 46*(1), 50–80. https://doi.org/10.1518/hfes.46.1.50_30392

[8] Rajaram, S., & Pereira-Pasarin, L. P. (2010). Collaborative memory: Cognitive research and theory. *Perspectives on Psychological Science, 5*(6), 649–663. https://doi.org/10.1177/1745691610388763

[9] Roediger, H. L., Meade, M. L., & Bergman, E. T. (2001). Social contagion of memory. *Psychonomic Bulletin & Review, 8*(2), 365–371. https://doi.org/10.3758/BF03196174

[10] Sun, J., Zhang, Z., Wang, M., Li, N., Lu, Z., Xiang, Y., Zhang, L., Zhang, Y., Wang, Q., & Fan, M. (2025). Chorus of the past: Toward designing a multi-agent conversational reminiscence system with digital artifacts for older adults. *Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*, Article 1031, 1–22. https://doi.org/10.1145/3706598.3713810

[11] Epperson, W., Bansal, G., Dibia, V., Fourney, A., Gerrits, J., Zhu, E., & Amershi, S. (2025). Interactive debugging and steering of multi-agent AI systems. *Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*, 1–15. https://doi.org/10.1145/3706598.3713581

[12] Liu, Y., Shah, V., Suh, S., Siangliulue, P., August, T., & Huang, Y. (2025). Perspectra: Choosing your experts enhances critical thinking in multi-agent research ideation. *arXiv preprint arXiv:2509.20553*. https://arxiv.org/abs/2509.20553

[13] Pareek, S., Govers, J., Kollerup, N. K., Wong, E., Velloso, E., & Goncalves, J. (2026). Sensemaking in multi-agent LLM interfaces: How users interpret transparency and trustworthiness cues. *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems*, 1–20. https://doi.org/10.1145/3772318.3791157

[14] Lim, H., Choi, D., Nam, S., Kim, B., & Hong, H. (2026). Understanding human–multi-agent team formation for creative work. *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems*, Article 70. https://doi.org/10.1145/3772318.3791166

[15] Sheng, R., Yang, Y., Shi, C., Lin, Y., Chen, Z., Qu, H., & Cheng, F. (2026). DiLLS: Interactive diagnosis of LLM-based multi-agent systems via layered summary of agent behaviors. *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems*, Article 1077, 1–17. https://doi.org/10.1145/3772318.3790815

[16] Quan, K., Albassam, D., Wu, M., Ding, Z., & Chin, J. (2026). Towards AI as colleagues: Multi-agent system improves structured ideation processes. *Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems*. Association for Computing Machinery.

[17] Ryu, J., Kim, K., Heo, D., Song, H., Oh, C., & Suh, B. (2025). Cinema Multiverse Lounge: Enhancing film appreciation via multi-agent conversations. *Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems*, 1–22. https://doi.org/10.1145/3706598.3713641

[18] Naik, S., Snellinger, A., Toombs, A. L., Saponas, S., & Hall, A. K. (2025). Exploring early adopters’ use of AI driven multi-agent systems to inform human-agent interaction design: Insights from industry practice. *Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems*. Association for Computing Machinery.

[19] Ghosh, P., & Rintel, S. (2025). YES AND: A generative AI multi-agent framework for enhancing diversity of thought in individual ideation for problem-solving through confidence-based agent turn-taking. *Extended Abstracts of the 2025 CHI Conference on Human Factors in Computing Systems*, 1–13. https://doi.org/10.1145/3706599.3720142
