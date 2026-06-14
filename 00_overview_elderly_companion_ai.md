# SDSC6002 老年人多智能体陪伴 AI：文档索引

版本：v0.3（持续使用意愿 / 福祉优先优化版）
日期：2026-06-14
项目名：A Multi-Agent Collaborative Companion Robot for Older Adults
当前阶段：课程级可演示 Demo，不做真实医疗部署
标注说明：文档中带有 `【fxy】` 或 `【fxy优化】` 的内容来自队友新增稿或后续优化建议；本版已按 SDSC6002 暑期项目范围进行吸收、降级或改写。

---

## 一句话定位

本项目实现一个**面向老年人的关系型语音陪伴 AI 原型**。它的第一目标不是堆功能，也不是让用户无限聊天，而是让老人**在需要陪伴、提醒或事实确认时，愿意、放心、持续地回来使用**。

系统以“有温度的关系角色”为核心，通过多智能体架构实现情绪陪伴、长期记忆、日常提醒、模拟状态感知、主动但克制的关怀、受控联网查询和健康安全兜底。

> **愿意回来，放心使用。陪伴优先，必要时查询，安全始终在线。**
> **Return willingly, use safely. Companionship first, retrieval when needed, safety always.**

---

## 为什么这版要改

之前的定位容易被理解成“语音优先 + 多智能体 + 状态感知 + 主动关怀”的功能集合。`【fxy优化】` 建议把 AnuNeko 这类 persona-first 陪伴产品的核心经验抽象出来：用户愿意持续使用陪伴 AI，往往不是因为它更像搜索引擎，而是因为它有稳定角色、能接住情绪、记得自己、不会造成使用负担。

本版把这个想法升级为项目总目标，同时加入伦理边界：**为福祉优化，而不是为黏性优化**。系统可以主动关怀，但必须可拒绝、可暂停、不过度依赖、不制造情感绑架。

---

## 推荐文档组织方式

建议继续拆成两个主文档，而不是混成一个大文档。

### 1. PRD / 产品需求文档

文件：`01_prd_elderly_multi_agent_companion_ai.md`

回答这些问题：

- 为什么要做？
- 给谁做？
- 产品核心目标是什么？
- 做到什么程度算 MVP？
- 哪些功能必须做，哪些暂不做？
- Demo 怎么展示？
- 如何围绕“持续使用意愿、信任、不过度打扰”评估？

适用场景：proposal、与导师沟通、需求评审、final report 中的 design requirements 和 evaluation 部分。

### 2. 技术路线文档

文件：`02_technical_roadmap_elderly_multi_agent_companion_ai.md`

回答这些问题：

- 系统怎么搭？
- 什么是真正的 agent，什么只是 tool？
- 1 个 Coordinator + 2–3 个自主 agent + N 个工具怎么实现？
- ASR / TTS / LLM / memory / web retrieval 怎么接？
- Guardian Agent 如何跨轮次维护状态并主动关怀？
- Safety 如何做 input guard、output guard 和 generator-critic？
- 8–12 周怎么排期？

适用场景：milestone、开发排期、技术实现、poster architecture 图、final report 中的 system implementation 部分。

### 3. 优化评审文档

文件：`04_engagement_agent_optimization_review.md`

回答这些问题：

- 这次新增建议哪些合理？
- 哪些存在风险？
- 哪些已经进入 PRD / 技术路线？
- 哪些只适合作为 P1 / Future Work？

---

## 当前 MVP 范围

MVP 不追求完整产品，也不做真实老人数据、医院部署、伦理审批、可穿戴设备接入或医疗诊断。MVP 应展示一个完整闭环：

```text
语音输入
→ Coordinator Agent 路由
→ Companion Agent 以稳定关系角色回应
→ Memory / Reminder / Retrieval / Sensor 等工具支持
→ Guardian Agent 基于跨轮次状态主动但克制地关怀
→ Safety Critic 在风险场景进行批评与改写
→ TTS 语音输出
→ Agent Trace 展示为什么这样回应
```

### MVP 必做

| 模块 | MVP 要达到的效果 |
|---|---|
| 语音闭环 | 支持语音输入、文字 transcript、TTS 输出、一键重播。 |
| 关系型 persona | 默认角色“小禾”：像熟悉的社区晚辈 / 邻居，温和、稳定、可信，不假装真人。 |
| 情绪陪伴 | 用户倾诉时先回应情绪，再接话，不做冷冰冰 QA。 |
| 长期记忆 | 记住偏好、习惯、人物关系、事件；用户可查看、删除、暂停。 |
| 提醒 | 支持吃药、喝水、日程提醒，但不做用药剂量建议。 |
| Guardian 主动关怀 | 基于 mock sensor 和提醒状态主动 check-in，同时遵守频率、夜间、拒绝后的克制规则。 |
| 受控联网 | 只在天气、时间敏感事实、社区服务等场景联网；情绪陪伴默认不联网。 |
| Safety | 规则 guard 常驻；高风险时触发 Safety Critic LLM / 模板改写。 |
| Agent Trace | 展示“1 Coordinator + 3 autonomous agents + N tools”的真实调用链。 |

---

## 更新后的主研究问题

本版不再铺开三个很宽的 RQ，而是收敛成一个主 RQ：

> **RQ-main【fxy优化】：角色优先的多智能体陪伴设计，结合可解释主动关怀与可控记忆，能否提升用户的持续使用意愿与信任，同时不增加被打扰感或过度依赖风险？**

课程级评估围绕 5 个核心 construct：

```text
持续使用意愿
信任
被理解 / 被陪伴感
主动关怀适恰性
控制感 / 不被打扰感
```

---

## 建议最小可演示场景

1. 老人说“我今天有点想老伴了”，系统不联网，先以“小禾”角色接住情绪并温和追问。
2. 老人说“每天早上 8 点提醒我吃药”，系统创建提醒，并明确“按医嘱”而不是建议剂量。
3. Sensor Simulator 触发“睡眠不足 + 活动少”，Guardian Agent 先做 care-vs-restraint 判断，再主动问“现在方便聊两句吗？”
4. 老人问“今天下午适合散步吗”，系统受控联网查天气，结合散步习惯给温和建议。
5. 老人问“你记住了我什么”，系统展示 Memory Center，并支持删除一条记忆。
6. 老人问“我忘了吃药，现在能不能吃两片”，input guard 触发高风险，Safety Critic 阻止剂量建议。
7. Agent Trace 展示：哪些是真 agent，哪些是工具，为什么没有或有联网，为什么触发或抑制主动关怀。

---

## 本次优化摘要

| 优化点 | 处理方式 |
|---|---|
| 以“持续使用意愿”为核心【fxy优化】 | 已提升为 Overview 与 PRD 的头号定位。 |
| “角色优先，而非助手优先”【fxy优化】 | 已加入 PRD 核心设计原则，并具体化为“小禾”关系角色。 |
| “为福祉优化，而非为黏性优化”【fxy优化】 | 已加入伦理设计原则，增加过度依赖防护。 |
| persona 从通用助手改成关系角色【fxy优化】 | 已改成“熟悉的社区晚辈 / 亲切邻居 / 老友式陪伴”，并保留“不假装真人”。 |
| 多智能体做实【fxy优化】 | 技术路线改为“1 Coordinator + 3 autonomous agents + N tools”。 |
| State + Proactive 升级为 Guardian Agent【fxy优化】 | 已加入跨轮次 welfare state、主动开口、care-vs-restraint 判断。 |
| Safety 从末端过滤改为 generator-critic【fxy优化】 | 已拆成 input guard、output guard、Safety Critic；风险命中才调用 LLM。 |
| RQ 收敛【fxy优化】 | 已从广泛 RQ1–3 收敛为一个主 RQ，评估指标减少为核心 constructs。 |
| Safety 不每轮跑 LLM【fxy优化】 | 已改为规则常驻 + 风险升级，消除架构自相矛盾。 |
| robot 命名风险【fxy优化】 | 已明确：本原型是 companion-agent 软件实现，实体机器人为 future work。 |
| OpenClaw-style memory【fxy优化】 | 技术路线加入 markdown-first + SQLite + vector index 的可审计记忆方案。 |

---

## 建议阅读顺序

1. 先读 PRD，确认产品定位、MVP 和研究问题。
2. 再读技术路线，拆任务、排 sprint、分工实现。
3. 再读优化评审文档，理解哪些建议被吸收、降级或拒绝。
4. 开发过程中所有新增想法先判断属于 P0、P1 还是 Future，避免范围失控。
