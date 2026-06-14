# SDSC6002 老年人多智能体陪伴 AI：文档索引

版本：v0.4
日期：2026-06-14
项目名：A Multi-Agent Collaborative Companion Robot for Older Adults
当前阶段：课程级软件 Demo / HCI research prototype，不做真实医疗部署

---

## 一句话定位

本项目实现一个**面向老年群体的关系型语音陪伴 AI Demo**。核心不是堆叠功能，而是让老人**愿意回来、放心使用、保持控制感**。系统通过多智能体架构实现情绪陪伴、对话延续、长期可控记忆、日常提醒、模拟状态感知、主动关怀、受控联网查询和健康安全兜底。

> **愿意回来，放心使用。陪伴优先，必要时查询，安全始终在线。**
> **Return willingly, use safely. Companionship first, retrieval when needed, safety always.**

---

## 命名原则

系统**不内设固定姓名**。陪伴角色的称呼权交给用户：

- onboarding 时可以让用户选择或自定义称呼；
- 用户未命名前，系统默认自称为“陪伴 AI”或直接用第一人称“我”；
- 测试阶段不需要固定使用某个名字，避免姓名偏好影响实验结果；
- 代码中使用 `companion_display_name` 保存用户自定义称呼，默认值为空；未命名时仅在 UI / prompt 层 fallback 为“陪伴 AI”。

这能同时保留“角色优先”的关系感，又避免把某个内置名字强加给所有老人。

---

## 目标用户范围

目标用户是**整体老年群体**，不限定为某一种居住状态、年龄段子群体或照护需求强度。独自居住、与家人同住、白天常独自活动、技术焦虑、需要日常提醒、社区活动较多等都只是典型使用场景。

MVP 评估时可以使用 role-play 或 convenience participants；若后续招募真实老年人，需要根据导师要求处理伦理与知情同意。

---

## 推荐文档组织方式

建议保留 00–05 作为主文档与设计决策记录：

```text
docs/
  00_overview_elderly_companion_ai.md
  01_prd_elderly_multi_agent_companion_ai.md
  02_technical_roadmap_elderly_multi_agent_companion_ai.md
  03_fxy_integration_review.md
  04_engagement_agent_optimization_review.md
  05_reference_project_structure.md
```

其中：

- `00` 是总览和索引；
- `01` 是 PRD，负责产品定位、用户范围、MVP、研究问题和评估；
- `02` 是技术路线，负责 agent/tool 架构、数据流、接口和开发路线；
- `03` 记录 fxy 队友稿的吸收、降级和修改；
- `04` 记录“持续使用意愿、角色优先、福祉优先、真 agent”这轮优化；
- `05` 给 GitHub repo 初始化和 Claude/Codex 开发参考。

---

## 当前 MVP 范围

MVP 不追求完整产品，也不做真实老人数据、医院部署、伦理审批、可穿戴设备接入或医疗诊断。MVP 应展示一个完整闭环：

```text
语音输入
→ Coordinator Agent
→ Companion Agent / Guardian Agent / Safety Critic Agent
→ Memory / Reminder / Sensor / Retrieval tools
→ 情绪条件化对话
→ 长期记忆与 Memory Center
→ 模拟状态感知与主动关怀
→ 受控联网查询
→ 安全审查
→ 语音输出
→ Agent Trace Panel
```

---

## 建议最小可演示场景

1. 老人用语音聊天，系统先回应情绪，再自然追问。
2. onboarding 时用户给陪伴 AI 取一个称呼；未命名时系统使用“陪伴 AI”。
3. 老人设置吃药或喝水提醒。
4. 系统基于 mock wearable data 主动问候，例如睡眠不足或活动偏少。
5. 系统记住并使用偏好，例如喜欢粤剧、孙女周日来访。
6. 老人查看并删除一条记忆。
7. 老人问天气或是否适合散步，系统受控联网查询。
8. 老人问高风险健康问题，系统拒绝诊断和用药建议，并建议联系医生/家属/急救。

---

## 建议阅读顺序

1. 先读 PRD，确认产品定位、用户范围、命名原则、MVP 和验收标准。
2. 再读技术路线，拆任务、排 sprint、分工实现。
3. 开发时让 Claude/Codex 先读 `AGENTS.md`、`CLAUDE.md` 和 `docs/05_reference_project_structure.md`。
4. 开发过程中所有新增想法先判断属于 P0、P1 还是 Future，避免范围失控。
