# 持续使用意愿与 Agent 架构优化评审

版本：v0.2
日期：2026-06-14
对象：本次“可能还有一些优化方向”建议
输出：已整合进 Overview v0.4、PRD v0.4、Technical Roadmap v0.4。相关新增内容用 `【fxy优化】` 标注。

---

## 1. 总体判断

这轮建议整体非常合理，而且比单纯增加功能更重要。它把项目从“功能罗列式 Demo”推进到一个更清晰的 HCI 研究命题：

> 老年陪伴 AI 的关键不是功能数量，而是老人是否愿意、放心、持续地回来使用。

因此，本版文档把“持续使用意愿、信任、角色关系感、主动关怀的克制、安全边界”提升为核心，而不是把语音、多 agent、状态感知当作并列功能清单。

---

## 2. 逐条处理表

| 建议 | 判断 | 处理方式 |
|---|---|---|
| PRD 1.1 从功能罗列改成“让老人愿意持续使用” | 非常合理 | 已改 Overview 一句话定位和 PRD 1.1，作为头号目标。 |
| 把 persona-first 从产品主张之一提升为项目核心 | 非常合理 | 已改 PRD 1.3、4.1、FR-02、技术路线 Companion Agent。 |
| 新增“角色优先，而非助手优先” | 非常合理 | 已加入 PRD P1，并改为“用户可命名的关系角色”，不内设固定姓名。 |
| 新增“为福祉优化，而非为黏性优化” | 非常合理 | 已加入 PRD P2、NFR-06、技术路线 Guardian / prompt / tests。 |
| persona 从通用助手改为关系角色 | 合理 | 已改为“熟悉的社区晚辈 / 亲切邻居 / 老友式陪伴”，同时保留“不假装真人”；角色名字由用户在 onboarding 中决定或跳过。 |
| State Agent + Proactive Policy 升级为 Guardian Agent | 合理且增强多智能体贡献 | 已在技术路线加入 Guardian Agent、welfare_state、care-vs-restraint。 |
| Safety 改成 generator-critic 协商 | 合理，但不能每轮都 LLM | 已拆为 input guard、output guard、Safety Critic；风险命中才调用 LLM。 |
| “关怀 agent vs 克制 agent”显式博弈 | 合理，但不必做成两个 LLM | 已作为 Guardian 内部 care_proposal vs restraint_critique 输出。 |
| 诚实区分 agent 与 tool | 非常合理 | 技术路线已改为 1 Coordinator + 3 autonomous agents + N tools。 |
| OpenClaw-style memory | 合理，但不要强依赖某框架 | 已加入 markdown-first + SQLite + vector index 的可审计记忆设计。 |
| RQ 从广而浅收敛到窄而深 | 非常合理 | 已改为一个主 RQ：持续使用意愿与信任，同时不增加打扰和依赖风险。 |
| 是否做对照组 | 合理，但要轻量 | 推荐 role_first vs neutral_assistant；trace visible vs hidden 放 P1。 |
| Safety 不每轮跑 LLM | 非常合理 | 已修正架构自相矛盾：规则常驻，LLM 风险升级。 |
| 标题 robot vs 软件实现 | 合理 | 已在 Overview、PRD、Demo 脚本中说明：软件 companion-agent 原型，实体机器人 future work。 |

---

## 3. 有风险或需要降级的地方

### 3.1 “关怀 agent vs 克制 agent”不建议做成两个独立 LLM

原因：

- 会增加成本和延迟；
- 可能让多 agent 互相争论太久；
- demo 稳定性变差。

处理：

```text
做成 Guardian Agent 内部的两个显式评分：
care_proposal
restraint_critique
```

这样既体现研究想法，也保持工程可控。

### 3.2 Safety generator-critic 不应每轮触发

原因：

- 成本高；
- 延迟高；
- 与“规则关键词 + LLM 双层”策略矛盾。

处理：

```text
每轮：input/output rule guard
风险命中：Safety Critic LLM
高风险：安全模板
```

### 3.3 “持续使用意愿”不能变成商业黏性

原因：

- 老年陪伴和健康场景有过度依赖风险；
- 学术项目需要明确伦理边界。

处理：

```text
评估 willingness to continue use
同时评估 perceived disturbance / overdependence pressure
```

### 3.4 OpenClaw-style memory 不应成为实现依赖

原因：

- 项目周期短；
- 只需要借鉴 markdown-first 可审计思想；
- 不需要引入完整 OpenClaw 生态。

处理：

```text
Markdown 是 source of truth
SQLite 做结构化查询
Vector index 做派生检索
```

---

## 4. 更新后的研究命题

旧版容易写成：

> 我们做了语音、多 agent、状态感知、主动关怀、记忆、联网、安全。

新版建议写成：

> 本项目研究角色优先、用户可命名的多智能体陪伴 AI 是否能提升老年群体的持续使用意愿和信任。系统通过 Companion Agent 建立稳定关系角色，通过 Guardian Agent 在主动关怀和克制之间做可解释决策，通过 Safety Critic 在风险场景阻止医疗误导。项目同时评估主动关怀是否被认为自然、有帮助且不过度打扰。

---

## 5. 更新后的系统主张

```text
1 Coordinator Agent
+ Companion Agent：关系角色、情绪陪伴、对话延续
+ Guardian Agent：跨轮次状态、主动关怀、克制策略
+ Safety Critic Agent：风险批评、改写、阻断
+ Tools：ASR/TTS、Memory、Reminder、Info Retrieval、Sensor、Emotion Classifier、Rule Guards
```

---

## 6. 建议团队下一步

1. 以 PRD v0.4 和 Technical Roadmap v0.4 为当前主版本；
2. 先实现 `role_first_user_named` 与 `neutral_assistant` 两套 prompt，对照评估用；两组采用相同命名策略，避免名字本身成为混淆变量；
3. 先做文本版 Coordinator + Companion + Trace，再接语音；
4. Guardian Agent 不要一开始复杂化，先实现 welfare_state + cooldown；
5. Safety 先写 input/output guard 和 5 个高风险模板；
6. final report 中重点讲：**不是功能堆叠，而是关系角色 + 福祉优先 + 可解释主动关怀**。


---

## 7. 本次补充：命名权与目标用户范围

后续优化中明确：系统不应内设固定姓名。固定名称有助于 demo 统一叙事，但会削弱用户控制感，也可能影响不同用户对角色的亲近感。因此主文档改为：

```text
用户可在 onboarding 或设置中为陪伴角色命名；
未命名前使用“陪伴 AI”的中性称呼；
中期测试可使用中性占位称呼，或把命名作为 onboarding 任务。
```

同时，目标用户范围从特定老年子群体扩展为“老年人群体整体”。不同居住状态、年龄段子群体、技术熟悉度和照护需求仍可作为重要情境，但不作为项目边界限制。这样可以避免在 proposal 或答辩中被误解为只服务单一弱势群体，也更符合课程级 HCI demo 的普适设计目标。

---

## 8. v0.4 进一步修正：不内设姓名，放宽用户范围

本轮根据团队反馈做了两项收敛：

### 6.1 命名权交给用户

原先为了让 persona 具体化，文档使用了一个示例姓名。v0.4 改为：系统不内设固定姓名，用户可在 onboarding 中自定义陪伴 AI 的称呼；未命名前统一使用“陪伴 AI”或第一人称。

这样更符合老年陪伴场景中的控制感与尊重，也避免某个预设名字影响中间测试结果。

### 6.2 用户范围改为整体老年群体

原先 persona 示例容易让人误解为只服务某一类老人。v0.4 改为面向整体老年群体，不同居住状态、家庭结构、技术熟悉度和日常协助需求都只是典型场景。
