# SDSC6002 老年人多智能体陪伴 AI：文档索引

版本：v0.1  
日期：2026-06-12  
项目名：A Multi-Agent Collaborative Companion Robot for Older Adults  
当前阶段：课程级可演示 Demo，不做真实医疗部署

---

## 一句话定位

本项目实现一个**面向老年人的网页端语音陪伴 AI Demo**。系统以情绪陪伴和对话延续为核心，通过多智能体架构实现长期记忆、日常提醒、模拟状态感知、主动关怀、受控联网查询和健康安全兜底。

> **陪伴优先，必要时查询，安全始终在线。**  
> **Companionship first, retrieval when needed, safety always.**

---

## 推荐文档组织方式

建议拆成两个主文档，而不是混在一个大文档里。

### 1. PRD / 产品需求文档

文件：`01_prd_elderly_multi_agent_companion_ai.md`

回答这些问题：

- 为什么要做？
- 给谁做？
- 做到什么程度算 MVP？
- 哪些功能必须做，哪些暂不做？
- Demo 怎么展示？
- 如何评估可用性、信任感、主动关怀是否合适？

适用场景：proposal、与导师沟通、需求评审、final report 中的 design requirements 和 evaluation 部分。

### 2. 技术路线文档

文件：`02_technical_roadmap_elderly_multi_agent_companion_ai.md`

回答这些问题：

- 系统怎么搭？
- agent 怎么拆分？
- 每个模块输入输出是什么？
- ASR / TTS / LLM / memory / web retrieval 怎么实现？
- 8–12 周怎么排期？
- 4 人团队怎么分工？

适用场景：milestone、开发排期、技术实现、poster architecture 图、final report 中的 system implementation 部分。

---

## 当前 MVP 范围

MVP 不追求完整产品，也不做真实老人数据、医院部署、伦理审批、可穿戴设备接入或医疗诊断。MVP 应展示一个完整闭环：

```text
语音输入
→ 多智能体协作
→ 情绪条件化对话
→ 长期记忆
→ 模拟状态感知
→ 主动关怀
→ 受控联网查询
→ 安全审查
→ 语音输出
```

---

## 建议最小可演示场景

1. 老人用语音聊天，系统先回应情绪，再自然追问。
2. 老人设置吃药或喝水提醒。
3. 系统基于 mock wearable data 主动问候，例如睡眠不足或活动偏少。
4. 系统记住并使用偏好，例如喜欢粤剧、孙女周日来访。
5. 老人查看并删除一条记忆。
6. 老人问天气或是否适合散步，系统受控联网查询。
7. 老人问高风险健康问题，系统拒绝诊断和用药建议，并建议联系医生/家属/急救。

---

## 建议阅读顺序

1. 先读 PRD，确认产品定位、MVP 和验收标准。
2. 再读技术路线，拆任务、排 sprint、分工实现。
3. 开发过程中所有新增想法先判断属于 P0、P1 还是 Future，避免范围失控。
