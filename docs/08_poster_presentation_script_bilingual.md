# Poster Presentation Script (5–8 Minutes)

**Poster title:** *Relationship-Aware Orchestration for Older-Adult Reminiscence*<br>
**Authors:** Fei Xiaoya, Su Zhikang, An Boxuan, Zhao Ziyi<br>
**Supervisor:** Yu Lu<br>
**Repository:** `github.com/zhikangSu/nekoneko`

## 使用说明

下面是一份约 6–7 分钟的双语对照讲稿。正式展示时选择英文版或中文版其中一种，不要把两种语言连续全部朗读，否则会超过 8 分钟。方括号内是指向海报的提示，不需要念出。

---

## 1. Opening and vision — 35 seconds

**English**

Good morning. Our project is called *Relationship-Aware Orchestration for Older-Adult Reminiscence*. We are building a user-named AI companion that helps older adults feel heard, remembered, safe, and in control. Our goal is not to maximize conversation or replace family, caregivers, or clinicians. It is to create the right kind of invitation to talk, with clear ways to pause, redirect, or stop.

**中文**

大家好，我们的项目叫做“面向老年回忆陪伴的关系感知编排”。我们希望构建一个由用户命名的 AI 陪伴者，让老年人感到自己被倾听、被记住，同时保持安全和自主。我们的目标不是让对话越多越好，也不是替代家人、照护者或医生，而是在合适的时刻给出合适的交流邀请，并让用户随时可以暂停、转向或停止。

---

## 2. Motivation — 50 seconds

[Point to Section 1: Why a Single Voice Is Not Enough.]

**English**

The problem begins with two unsatisfactory extremes. A single chatbot often asks direct questions, which can make reminiscence feel like an interview. But an unconstrained group of personas may become noisy, artificial, repetitive, or intrusive. This is especially important when the topic involves family, bereavement, health, privacy, or regret. So our central question is not simply how to add more agents. It is how to coordinate a small and legible social scene that makes it easier for an older adult to join a memory conversation.

**中文**

这个问题来自两个都不理想的极端。单一聊天机器人经常直接提问，容易让回忆交流像一次采访；但如果多个角色不受约束地一起说话，又会显得嘈杂、虚假、重复，甚至侵犯边界。当话题涉及家人、离世亲友、健康、隐私或遗憾时，这个问题更加明显。因此，我们真正研究的不是简单增加 Agent 数量，而是如何组织一个小而清晰的社交场景，让老年人更自然地进入回忆对话。

---

## 3. Research questions and contribution — 55 seconds

[Point to Sections 2 and 3.]

**English**

We ask three questions. First, which relationship roles should speak, wait, follow up, summarize, or stop for a given topic and preference? Second, can a brief role-to-role cue feel more natural and lower-pressure than a cold direct question? Third, how can differentiated roles cooperate without creating noise, inauthenticity, overload, or boundary violations? Our contribution is a deterministic and traceable orchestration policy. It selects the smallest useful cast—at most three visible roles—and treats silence, deferral, and stopping as valid system decisions.

**中文**

我们提出三个研究问题。第一，针对不同话题和偏好，哪些关系角色应该发言、等待、追问、总结或停止？第二，简短的角色间线索，是否会比直接提问更加自然、压力更低？第三，差异化角色如何协作，同时避免噪声、虚假感、认知负担和边界侵犯？我们的主要贡献是一套确定性、可追踪的编排策略。它每轮只选择最少但有用的角色，最多三个，并把静默、延后和停止也视为正确的系统决策。

---

## 4. Core mechanism and architecture — 90 seconds

[Point to Section 4 and follow the flow from left to right.]

**English**

The workflow starts with text or voice input. An input guard first checks risk. The CoordinatorAgent then chooses a route, applies a bounded tool policy, and passes eligible reminiscence turns to the relationship scheduler. The scheduler reads the topic, user preference, consented memory, sensitivity, and stopping signals. It then classifies the scene, selects one to three useful roles, stages a short cue, gives one gentle invitation, and finally yields the floor to the user.

The CompanionAgent produces the user-facing response. An output guard checks the draft, and every turn returns an Agent Trace showing the route, risk, agents, tools, guards, role decisions, memory state, retrieval state, and whether short conversation history was used. Separate supporting paths handle reminders, memory authorization, controlled weather retrieval, and voice services. Simulated sensor signals are normalized into StateEvents before GuardianAgent decides whether to check in, defer, stay silent, or escalate safely.

**中文**

整个流程从文字或语音输入开始。输入守卫先检查风险，CoordinatorAgent 再决定路由和受限的工具策略。符合条件的回忆话题会进入关系调度器。调度器读取话题、用户偏好、经过同意的记忆、敏感程度和停止信号，然后完成五步：分类场景、选择一到三个有用角色、组织简短线索、给出一个温和邀请，最后把话语权交还给用户。

CompanionAgent 负责生成用户可见的回复，输出守卫检查草稿。每轮都会返回 Agent Trace，展示路由、风险、Agent、工具、守卫、角色选择、记忆与检索状态，以及是否使用了短期对话历史。提醒、记忆授权、天气检索和语音由独立服务支持。模拟传感器信号必须先转换成 StateEvent，GuardianAgent 才会决定主动关怀、延后、静默或安全升级。

---

## 5. Agents, roles, and user-facing functions — 100 seconds

[Point to Section 5.]

**English**

A key distinction is that not every component is an agent. We use four autonomous agents: CoordinatorAgent for routing, CompanionAgent for relational dialogue, GuardianAgent for restrained proactive care, and SafetyCriticAgent for risky or highly uncertain content. The eight visible relationship-role options are not eight independent LLM agents. They are bounded conversational functions scheduled through the companion layer.

These options include a Same-Age Peer for era resonance without claiming a real shared past; a Curious Junior for one gentle follow-up; a Middle-Age Bridge for carrying experience forward; an Elder Mentor for low-judgment reflection; a Theme Companion for culture and interest; a Memory Organizer that summarizes only with consent; a Boundary Guardian that pauses or redirects; and a No Relationship Role option that returns to the user-named companion.

The current prototype also includes persistent naming and settings, multi-turn chat, topic cards, manual role control, real or mock ASR and TTS, transparent memory cards, reminders with date, time, and frequency, simulated care events, controlled weather retrieval, caregiver summaries, and a detailed Agent Trace. Research-only evaluation export remains implemented but is hidden from the normal coursework interface.

**中文**

这里有一个重要区别：并不是每个组件都叫 Agent。系统有四个自主 Agent：负责路由的 CoordinatorAgent、负责关系型对话的 CompanionAgent、负责克制式主动关怀的 GuardianAgent，以及只在风险或高不确定性时介入的 SafetyCriticAgent。八个可见关系选项并不是八个独立 LLM Agent，而是由陪伴层调度的受限对话功能。

这些选项包括：进行年代语境共鸣但不虚构共同经历的同龄共鸣者；一次只做一个温和追问的晚辈好奇者；承接经验的中年传承者；低评判反思的长辈引导者；围绕文化和兴趣展开的主题陪伴者；只在用户同意后整理内容的回忆整理者；负责暂停和转向的边界守护者；以及关闭关系角色、返回用户命名陪伴 AI 的“不使用关系角色”。

当前原型还实现了持久化命名与设置、多轮聊天、话题卡、手动角色控制、真实或 mock 的语音识别与合成、透明记忆卡、包含日期时间和频率的提醒、模拟关怀事件、受控天气检索、照护摘要和完整 Agent Trace。研究用评估导出仍保留在代码中，但默认不出现在课程交付界面。

---

## 6. Prototype evidence and evaluation — 80 seconds

[Point to Sections 6 and 7.]

**English**

The screenshot demonstrates that relationship-cued dialogue and its trace are running together in the current prototype. The trace shows the `relationship_cueing` route, selected and silent roles, risk, memory, retrieval, and boundary decisions. For engineering validation, we reran the full suite on 22 July: all 382 backend tests passed, and the Next.js production build also passed. These tests are offline and do not call paid APIs.

For future user evaluation, we propose three conditions: C1 is a direct question from one companion, C2 is a fixed role or fixed two-role prelude, and C3 is dynamic topic-aware orchestration. We would compare content, subjective experience, behavior, and boundary events. Importantly, these are planned study conditions. We do not yet claim that C3 has been proven more natural or clinically beneficial.

**中文**

海报中的截图证明，关系线索对话和对应的追踪面板已经在当前原型中同时运行。Trace 会显示 `relationship_cueing` 路由、发言与静默角色、风险、记忆、检索和边界决策。工程验证方面，我们在 7 月 22 日重新运行了完整测试：382 个后端测试全部通过，Next.js 生产构建也通过。所有自动测试均离线运行，不调用付费 API。

未来的用户评价计划比较三个条件：C1 是单一陪伴者直接提问，C2 是固定角色或固定双角色开场，C3 是根据话题动态编排。评价会同时观察内容、主观体验、行为和边界事件。需要强调的是，这些仍是计划中的研究条件；我们尚未声称 C3 已经被证明更自然，也没有声称任何临床效果。

---

## 7. Ethics, limitations, and next step — 55 seconds

[Point to Section 8.]

**English**

Our safety boundary is part of the interaction design, not an appendix. Roles never claim real kinship, a real shared history, or the identity of a deceased person. The system does not diagnose illness, change medication dosage, dispatch emergency services, or notify a real caregiver. Memory is visible and controllable, and proactive care can remain silent or be refused.

This is a completed course-level software prototype, not a clinical or production system. Sensors are simulated, providers are configurable, and real older-adult outcomes have not yet been established. The next research step is to refine role labels, tone, cue length, and acceptable topic-role pairings with older adults, and then run the C1/C2/C3 comparison under appropriate ethics approval.

**中文**

我们的安全边界不是附录，而是交互设计本身。所有角色都不会冒充真实亲属、虚构共同经历或扮演逝者。系统不诊断疾病、不改变药量、不拨打真实急救电话，也不通知真实照护者。记忆是可见、可控的，主动关怀可以保持静默，也可以被用户拒绝。

这是一个已经完成的课程级软件原型，但不是临床或生产系统。传感器是模拟的，provider 可以配置，真实老年用户效果尚未建立。下一步研究是与老年参与者共同优化角色名称、语气、线索长度和话题匹配，并在完成相应伦理审批后进行 C1/C2/C3 比较。

---

## 8. Closing — 25 seconds

**English**

To conclude, the value of this system is not that more voices speak. It is that the right role speaks at the right moment, while the system knows when to wait, summarize, redirect, or stop. Our vision is simple: return willingly, use safely—companionship first, retrieval when needed, and safety always. Thank you.

**中文**

最后，这个系统的价值不在于让更多声音一起出现，而在于让合适的角色在合适的时刻发言，并让系统知道什么时候等待、总结、转向或停止。我们的愿景是：愿意回来，放心使用；陪伴优先，必要时查询，安全始终在线。谢谢大家。

---

## Possible Q&A / 可能的提问

### Why use multiple roles instead of one stronger model?

The roles are not intended to increase raw model capability. They make relational stance, turn-taking, and boundary behavior explicit and testable. The scheduler can also choose only one role or no relationship role at all.

这些角色不是为了提升模型的参数能力，而是把关系立场、轮次控制和边界行为变得明确、可测试。调度器也可以只选择一个角色，或者完全不使用关系角色。

### Are the roles separate LLM agents?

No. The visible roles are bounded relationship functions. The system has four autonomous agents; the current relationship cueing is deterministic and auditable.

不是。可见角色是受限的关系功能。系统有四个自主 Agent，当前关系线索由确定性、可审计的策略生成。

### Does the system always use real APIs?

No. It supports both real and fake/mock providers. Offline demo mode is the default, while real MiMo language and voice providers and Open-Meteo retrieval can be enabled through local configuration. Secrets are never committed.

不是。系统同时支持真实和 fake/mock provider。默认是离线 demo；本地配置后可以启用 MiMo 语言与语音模型和 Open-Meteo 检索，密钥不会提交到仓库。

### What has been evaluated?

Engineering behavior has been evaluated through 382 backend tests and a successful frontend production build. The C1/C2/C3 older-adult study is a proposed next step, not a completed outcome study.

目前完成的是工程行为验证，包括 382 个后端测试和成功的前端生产构建。面向老年参与者的 C1/C2/C3 研究是下一步计划，不是已经完成的效果实验。
