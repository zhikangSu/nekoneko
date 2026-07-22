# QAQ 项目状态与海报精修说明

> 面向海报设计、内容精修与课堂展示的当前实现说明<br>
> 核对日期：2026-07-22<br>
> 权威开发仓库：`Freyalilith/QAQ`<br>
> 对外展示镜像：`zhikangSu/nekoneko`

## 1. 这份文档解决什么问题

本文件不是早期需求清单，而是根据当前代码、界面、测试和海报状态整理的交付快照。队友精修海报时，应优先以本文件、当前海报 HTML 和项目报告为准；`docs/00`–`docs/06` 仍用于解释项目最初的产品边界和开发过程，其中部分“下一阶段”描述已经被当前实现超越。

当前可直接使用的材料：

| 材料 | 路径 | 用途 |
|---|---|---|
| A0 海报源文件 | `output/poster/QAQ_academic_poster_framework.html` | 版式、文字和图示的唯一可编辑海报源 |
| 海报预览 | `output/poster/QAQ_academic_poster_framework_preview.pdf` / `.png` / `.jpg` | 审阅、打印前检查与群内分享 |
| 实机截图 | `docs/report_assets/2026-07-20/` | 海报中的系统证据与报告插图 |
| 双语讲稿 | `docs/08_poster_presentation_script_bilingual.md` | 5–8 分钟课堂讲解 |
| 英文项目报告 | `docs/09_course_project_report.md` | 完整技术、研究背景和参考文献 |
| 功能测试报告 | `output/reports/QAQ_功能与系统测试报告_2026-07-20.docx` | 可交付的功能与系统测试记录 |

## 2. 一句话介绍

QAQ is a **relationship-aware, multi-agent reminiscence companion for older adults**. It uses a user-named companion, a deterministic relationship-role scheduler, transparent memory controls, restrained proactive care, controlled retrieval, voice services, layered safety, and an inspectable Agent Trace to help older adults feel heard, remembered, safe, and in control.

中文概括：这是一个面向老年人的关系感知多智能体回忆陪伴原型。核心不是“让更多角色一起说话”，而是根据话题、偏好和边界，决定谁应该说、等待、追问、总结或停止。

产品口号：

> **Return willingly, use safely. Companionship first, retrieval when needed, safety always.**<br>
> **愿意回来，放心使用。陪伴优先，必要时查询，安全始终在线。**

## 3. 项目定位与研究问题

### 3.1 设计动机

单一陪伴者直接提问容易产生“被采访”的压力；没有协调的多角色对话又可能显得嘈杂、虚假、抢话或越界。因此，本项目把多智能体价值重新定义为一个**编排问题**：用最少但有用的关系线索，帮助用户自然进入回忆，同时保留拒绝、暂停、转向和停止的权利。

### 3.2 海报中的三个研究问题

1. **Relationship orchestration:** 针对具体话题和偏好，哪些角色应当发言、等待、追问、总结或停止？
2. **Social cueing:** 简短的角色间线索，是否比直接提问更自然、压力更低？
3. **Role interaction:** 差异化角色如何合作，同时避免噪声、虚假感、认知负担和边界侵犯？

### 3.3 当前能够诚实声称的贡献

- 定义了七种关系功能与一个“不使用关系角色”选项。
- 实现了可复现、可审计的确定性角色调度策略，每轮最多选择三个角色。
- 实现了可运行的全栈原型，覆盖聊天、语音、记忆、提醒、主动关怀、受控检索、安全和追踪。
- 为后续 C1/C2/C3 比较研究准备了可观测字段、场景和评价维度。

不能声称：已经证明临床效果、减少孤独、改善认知、完成 65+ 真实参与者实验，或具备生产级医疗/急救能力。

## 4. 当前系统结构

```text
Text / Voice Input
  → InputRuleGuard
  → CoordinatorAgent: route, risk, bounded tool policy
  → Relationship scheduler: topic, roles, cue style, silence/stop
  → CompanionAgent: user-facing response
  → OutputRuleGuard
  → Final response + Agent Trace

Supporting paths
  StateEvent → GuardianAgent → check_in / defer / silent_log / safety_escalation
  Risk or high uncertainty → SafetyCriticAgent
  Coordinator decision → Memory / Reminder / Retrieval / Voice services
```

### 4.1 四个自主 Agent

| Agent | 职责 | Trace 中的证据 |
|---|---|---|
| `CoordinatorAgent` | 决定路由、风险等级和受限工具调用 | Route、Agents、Tools、Guards |
| `CompanionAgent` | 生成温和、关系优先的用户可见回复 | Mode、Memory、History use |
| `GuardianAgent` | 根据 StateEvent 决定关怀、延后、静默或安全升级 | StateEvent、Reason、Cooldown |
| `SafetyCriticAgent` | 仅在风险或高不确定性时复核 | Risk level、Safe rewrite |

注意：`RelationshipOrchestratorAgent` 是代码中的确定性编排组件；海报应继续把七个关系角色描述为**可见角色/关系功能**，不要写成七个独立 LLM Agent。

### 4.2 八个用户可见选项

| Role | 作用 | 必须保留的边界 |
|---|---|---|
| Same-Age Peer | 年代语境共鸣 | 不声称真实年龄或共同经历 |
| Curious Junior | 一次一个轻量追问 | 不审问、不幼儿化 |
| Middle-Age Bridge | 承接并传递经验 | 不冒充真实家属 |
| Elder Mentor | 低评判的人生反思 | 不要求用户“输出智慧” |
| Theme Companion | 围绕戏曲、文化、旧物等建立共同语言 | 用户转题或拒绝时停止 |
| Memory Organizer | 忠实整理用户已经说过的内容 | 保存前确认，不虚构 |
| Boundary Guardian | 在悲伤、健康、隐私和依赖风险下暂停或转向 | 不扮演逝者、不诊断、不改药量 |
| No Relationship Role | 关闭关系角色，由用户命名的陪伴 AI 直接回应 | 与其他手动角色互斥 |

## 5. 已实现的用户功能

| 功能 | 当前状态 | 海报如何表达 |
|---|---|---|
| 用户命名与设置 | 已实现，刷新后保留 | User-named companion and persistent preferences |
| 普通陪伴聊天 | 已实现，可用真实或 fake LLM | Relationship-first multi-turn dialogue |
| 多轮上下文 | 已实现，Trace 显示 `conversation_history_used` | Short-history use is inspectable |
| 关系感知回忆 | 已实现，路由 `relationship_cueing` | Topic-aware role selection and brief social cueing |
| 手动角色控制 | 已实现，最多三项，“不使用”互斥 | Manual override and opt-out |
| 今日话题场 | 已实现，含不感兴趣和排序逻辑 | Low-pressure topic entry |
| ASR / TTS / 自动朗读 / 语速 | 已实现 mock 与真实 provider 接口 | Configurable text and voice interaction |
| Agent Trace | 已实现，含历史、角色、工具、守卫、检索与记忆状态 | Inspectable orchestration decisions |
| Memory Center | 已实现查看、授权、编辑、删除、暂停 | Transparent and user-controlled memory |
| Reminder | 已实现日期、时间、频率、试触发、确认、删除 | Reminders remain separate from autobiographical memory |
| SensorAdapter + Guardian | 已实现模拟信号、StateEvent 和克制式关怀 | Proactive care can defer or remain silent |
| Controlled retrieval | 已实现 mock / Open-Meteo 天气路径 | Retrieval only for time-sensitive external facts |
| 照护摘要 | 已实现并保留导航入口 | Mock caregiver-facing summary; no real notification |
| 评估导出 | 后端与页面代码保留，交付 UI 默认隐藏 | Research infrastructure, not a headline coursework feature |
| Demo video checklist | 不作为当前产品界面展示 | 不应出现在最终海报的功能列表中 |

## 6. Provider、模型与运行边界

默认配置是离线且不产生付费调用：

```text
DEMO_MODE=true
LLM_PROVIDER=fake
ASR_PROVIDER=mock
TTS_PROVIDER=mock
RETRIEVAL_PROVIDER=mock
```

真实 provider 仅在 `DEMO_MODE=false`、对应 provider 被选中且本地存在有效密钥时启用：

| 能力 | Provider | 当前默认模型/服务 |
|---|---|---|
| LLM | `xiaomimimo` | `mimo-v2.5` |
| ASR | `xiaomimimo` | `mimo-v2.5-asr` |
| TTS | `xiaomimimo` | `mimo-v2.5-tts`, voice `mimo_default` |
| Weather retrieval | `open_meteo` | Open-Meteo，无需 API key |

API key 只存在本地 `.env`，不会进入 GitHub。测试始终使用 fake/mock provider，不调用付费 API。海报应写“supports configurable real and mock providers”，不应写成“所有场景始终调用真实 API”。

## 7. 当前工程证据

2026-07-22 在本机重新验证：

- Backend: **382 tests passed**，1 个依赖弃用 warning。
- Frontend: Next.js production build passed，包括编译、lint 和 TypeScript 检查。
- 当前海报为 **A0 landscape**，HTML 源和 PDF/PNG/JPG 预览均已生成。
- 自动测试不调用真实 LLM、ASR、TTS 或外部检索。

这些证据证明当前实现的一致性和课堂演示准备度，不证明真实老年用户体验效果、生产可靠性或临床效果。

## 8. 海报现有八个正文部分

1. **Why a Single Voice Is Not Enough**：解释单一直接提问与无协调多角色的两类问题。
2. **Research Questions**：提出角色编排、社交线索和角色协作三个问题。
3. **Three Mechanisms, One Boundary**：概括角色分类、确定性调度和可追踪评估，并强调福祉优先、角色不冒充真人、安全边界。
4. **Relationship-Aware Orchestration**：展示输入、守卫、Coordinator、关系调度、角色线索、输出守卫和 Trace 的五阶段流程。
5. **Agents, Visible Roles & Supporting Services**：区分四个 Agent、八个可见选项和用户功能。
6. **Implemented Prototype Evidence**：用真实界面截图证明关系路由、角色线索和 Agent Trace 已运行。
7. **Evaluation Protocol & Current Evidence**：提出 C1 直接提问、C2 固定角色、C3 动态编排的比较框架，并明确当前只有工程证据。
8. **Ethics, Limitations & Next Steps**：说明不冒充、不静默保存、不诊断、不真实急救，以及后续需要真实老年参与者验证。

这八部分已经覆盖“问题—研究问题—机制—系统—功能—实机证据—评价—愿景与边界”的完整叙事。精修时可压缩重复文字、放大关键流程与截图，但不建议删除第 7、8 部分，否则海报会变成纯产品宣传而缺少研究设计和诚实边界。

## 9. 可直接用于海报的英文文案

### Short abstract

> We present a relationship-aware reminiscence companion for older adults. Rather than maximizing the number of speaking personas, the system uses a deterministic scheduler to select the smallest useful set of relationship roles, expose their decisions through Agent Trace, and preserve user control over memory, proactive care, retrieval, and stopping.

### Three contributions

1. **Interaction contribution:** brief, low-pressure social cues that invite rather than interrogate.
2. **System contribution:** auditable orchestration across four autonomous agents, eight visible role options, and bounded services.
3. **Evaluation contribution:** a C1/C2/C3 protocol connecting self-report, behavior, content, boundary events, and trace evidence.

### Honest evidence statement

> The current evidence establishes implementation consistency and demo readiness: 382 backend tests pass and the frontend production build succeeds. User-experience and clinical outcomes have not yet been established.

### Closing line

> The goal is not more conversation. It is the right role, at the right moment, with a clear way for the older adult to pause, redirect, or stop.

## 10. 精修时必须保持一致的事实

- 作者顺序：**Fei Xiaoya · Su Zhikang · An Boxuan · Zhao Ziyi**。
- 导师：**Yu Lu**。
- 展示单位：City University of Hong Kong；合作单位可保留文字，当前只展示 CityU logo。
- 海报仓库入口：`github.com/zhikangSu/nekoneko`。
- 正式题目：**Relationship-Aware Orchestration for Older-Adult Reminiscence**。
- 当前软件证据：**382 / 382 backend tests** 与 frontend production build passed。
- 可见角色是关系功能，不是七个独立自主 Agent。
- 真实 provider 是可配置能力；默认 demo 与测试均为 fake/mock。
- 研究参与者效果尚未建立，不能把计划中的 C1/C2/C3 写成已完成实验结果。

## 11. 推荐的队友协作方式

1. 只编辑 `output/poster/QAQ_academic_poster_framework.html`，不要直接改 PDF/PNG/JPG。
2. 优先做版式层面的精修：字号层级、行距、列间平衡、截图裁切、图示对齐和页脚对称。
3. 文案删减以本文件第 8–10 节为约束，避免改坏 Agent/Role/Tool 的概念边界。
4. 每次修改后重新生成 A0 预览，并检查标题、作者、单位、仓库入口和页脚是否遮挡。
5. 最终提交前再次运行 `make test`，并把测试数字更新到海报、讲稿和报告中的同一版本。

## 12. 项目边界

该项目是课程级 HCI 软件原型，不是医疗产品、临床干预、生产系统或真实急救服务。传感器为模拟输入，照护摘要不通知真实家属，系统不诊断、不改药、不拨打急救电话，也不以“陪伴”为理由制造依赖。
