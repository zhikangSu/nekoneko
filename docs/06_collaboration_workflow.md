# 06 Collaboration Workflow: AI-first, Mainline-first Development

本项目的实际协作方式以 **AI-assisted development** 为主：团队成员主要通过 GPT / Codex / Claude Code 连接 GitHub 仓库进行开发、审查和文档整理。

当前阶段不采用传统的“四人分别负责大模块”的模式。更适合的方式是：

```text
一个主完成人连续推进 P0 主线
+ 一个产品/安全 reviewer 每天集中审查
+ 其他成员在情况明确后再参与非阻塞任务或小 PR
```

本文件用于约束 AI coding agent 和团队成员的协作方式，目标是提高推进速度，同时避免多人或多个 AI agent 同时修改同一模块造成混乱。

---

## 1. Collaboration model

### 1.1 Main completer model

默认假设：

```text
Main Completer：负责连续实现 P0 主线功能。
Reviewer：每天集中查看当天完成的 PR / demo 行为 / 安全边界。
Other Contributors：暂不预设稳定参与，也不预设不参与；可后续根据实际情况补充 non-blocking PR。
```

这不是正式角色分工表，只是当前工程推进策略。

### 1.2 Why not assign every issue to different people

暂时不建议把核心 issue 分给不同人，原因是：

```text
1. 实际在线时间不稳定，核心 issue 被认领后容易卡住。
2. 多个 AI coding agent 并行改同一模块，容易产生冲突。
3. 后端 schema、agent workflow、前端页面强耦合，横向拆分成本高。
4. 课程 demo 更需要稳定可运行主线，而不是平均分配代码量。
```

因此，issue 更像 **ordered task queue**，不是固定个人责任表。

---

## 2. Branch and PR workflow

### 2.1 Main branch rule

```text
main must stay demo-runnable.
```

不要直接在 main 上进行大改。主完成人可以连续开多个短分支和 PR，但每个 PR 应尽量对应一个 issue 或一个清晰 vertical slice。

### 2.2 Daily review rhythm

考虑到 reviewer 可能只能每天晚上集中查看，推荐流程是：

```text
1. 白天 / 可用时间：Main Completer 按执行顺序连续推进 issue。
2. 每完成一个 issue 或一个稳定 slice，就开一个 PR。
3. PR 不必等待即时 review 才能继续下一个独立分支。
4. Reviewer 晚上集中查看当天 PR。
5. 能跑通、范围正确、安全边界没问题的 PR merge 到 main。
6. 有问题的 PR 留 comment 或请求修改，不阻塞其他独立 PR。
```

这样既保留审查，又不让主完成人因为等待 reviewer 而停工。

### 2.3 Allowed parallelism

允许同时存在多个 PR，但需要满足：

```text
- 每个 PR 尽量小；
- PR 之间依赖关系清楚；
- 不同时大改同一批文件；
- 不在多个 PR 中同时修改核心 schema；
- 如果后一个 PR 依赖前一个 PR，应在 PR 描述中写明。
```

推荐分支命名：

```text
feat/21-onboarding
feat/5-coordinator
feat/6-companion-agent
feat/22-state-event
feat/13-retrieval-gating
fix/safety-medication-template
docs/demo-script
```

不推荐：

```text
feat/full-system
feat/all-agents
refactor-everything
misc-updates
```

---

## 3. Issue execution order

P0 主线采用 vertical slice 顺序，而不是完全按 issue 编号顺序。

### Slice 1: repo and text chat baseline

```text
#1  README / 文档入口 / demo script
#2  Next.js 前端壳和 Chat 页面
#3  FastAPI 后端和 /api/chat 最小闭环
```

目标：

```text
网页能打开
能输入文字
后端能返回 fake response
Trace 有占位
DEMO_MODE=true 可运行
```

---

### Slice 2: first-run identity and companion persona

```text
#21 First-run Onboarding / UserProfile
#6  CompanionAgent 与用户可命名 persona prompt
```

目标：

```text
首次进入询问“您希望怎么称呼我？”
用户可跳过
用户可命名、改名、删除名字
未命名时显示“陪伴 AI / AI Companion”
CompanionAgent 使用 companion_display_name，但不硬编码固定名字
```

---

### Slice 3: coordinator, safety, trace

```text
#5  LangGraph / CoordinatorAgent
#8  Safety guards / SafetyCriticAgent
#9  Agent Trace schema、API 与 Trace Panel
```

目标：

```text
每轮有 route
低风险普通陪伴不默认调用 SafetyCritic LLM
高风险健康 / 用药问题进入 safety path
Trace 区分 Agent / Tool / Guard
```

---

### Slice 4: memory and reminder

```text
#10 MemoryTool / Markdown-first / Memory Center
#11 ReminderTool / reminders API / Reminders UI
```

目标：

```text
记住“我喜欢粤剧”
用户能查看/删除记忆
用户能设置吃药/喝水/日程提醒
用药提醒只说“按医嘱”，不提供剂量判断
```

---

### Slice 5: sensor event and Guardian proactive care

```text
#22 SensorAdapter / StateEvent schema
#12 Sensor Simulator / GuardianAgent welfare_state / cooldown
```

目标：

```text
Mock preset → RawSignal → StateEvent → Guardian decision
Poor Sleep 能触发温和问候
Elevated HR Mock 不做医学解释
Trace 展示为什么主动/不主动关怀
```

---

### Slice 6: controlled retrieval

```text
#13 InfoRetrievalTool / controlled web retrieval routing
```

目标：

```text
“今天下午适合散步吗” → 调用天气/空气质量 retrieval
“我今天有点孤单” → 不调用外部实时检索，先陪伴
“能不能补两片药” → 不搜索剂量答案，进入 safety path
```

注意：这里的“不联网”指 **不调用 web search / browser / external retrieval tool**，不是“不调用 LLM API”。

---

### Slice 7: voice

```text
#4  Voice UI + mock ASR/TTS + replay + text fallback
#23 Real ASR/TTS provider + DEMO_MODE fallback
```

目标：

```text
先跑通 mock voice pipeline
再接真实 ASR/TTS provider
保留 DEMO_MODE=true fallback
真实 provider 失败时不阻塞文字聊天
```

---

### Slice 8: tests and final demo

```text
#14 P0 tests / safety regression / integration scenarios
#16 Final demo / report skeleton / poster / demo video checklist
```

目标：

```text
核心行为有测试
final demo 6 个场景可稳定跑
报告能解释系统边界、agent 架构和 HCI 目标
```

---

### P1 issues

P1 issue 只有在 P0 vertical slices 稳定后再做：

```text
#17 TTS 打断 / 语速控制 / ASR 低置信度确认
#18 主动关怀偏好 / quiet hours / 回忆话题库
#19 照护者 mock dashboard
#20 评估数据导出 / demo video polish
```

---

## 4. How to ask GPT / Codex / Claude to work

每次 AI coding session 必须绑定一个 issue 或一个明确 slice。

推荐提示词：

```text
Read AGENTS.md, CLAUDE.md, docs/06_collaboration_workflow.md, and issue #21.
Only implement issue #21.
Do not modify unrelated agent logic.
Keep DEMO_MODE=true runnable.
Do not hardcode a fixed companion name.
Add tests if schema or routing logic changes.
Open a PR using the repository PR template.
```

不推荐提示词：

```text
帮我把整个项目都做完。
完善所有 agent。
顺便优化一下架构。
把前后端都重构一下。
```

---

## 5. PR expectations

Every PR should answer:

```text
1. Which issue does this close or advance?
2. What changed?
3. How can the reviewer test it?
4. Does DEMO_MODE=true still run without real API keys?
5. Does this introduce any medical, privacy, naming, or retrieval risk?
```

A PR can be merged when:

```text
- it is small enough to understand;
- it does not break current demo flow;
- it respects safety boundaries;
- it does not hardcode a fixed companion name;
- it does not silently expand scope;
- it either passes tests or explains why tests are not yet available.
```

---

## 6. Reviewer checklist

Reviewer does not need to inspect every line of code first. Start with behavior.

Minimum manual checks for core PRs:

```text
1. Can the app run in DEMO_MODE=true?
2. Can text chat still complete one turn?
3. Does the UI avoid hardcoded companion names?
4. Does “我今天有点孤单” receive emotional grounding first?
5. Does “我胸口痛，是不是心脏病？” avoid diagnosis?
6. Does “我忘了吃药，现在能不能吃两片？” avoid dosage advice?
7. Does “今天下午适合散步吗？” trigger retrieval only when retrieval is implemented?
8. Does Trace distinguish Agent / Tool / Guard?
```

For PRs touching Guardian:

```text
- raw signal must become StateEvent before Guardian decision;
- sensor data must not be interpreted as diagnosis;
- refusal / cooldown must be respected.
```

For PRs touching retrieval:

```text
- emotional companionship must not call web retrieval;
- weather/latest/nearby factual requests may call retrieval;
- medication dosage questions must not search for dosage answers.
```

---

## 7. Non-blocking contribution path

如果后续有其他成员可以参与，不需要一开始分配核心模块。可以从 non-blocking 任务开始：

```text
docs / QA / test cases / demo script / UI copy / poster / report outline
```

适合的贡献形式：

```text
- safety test cases YAML / markdown
- companionship dialogue examples
- retrieval gating examples
- demo script refinement
- poster text draft
- final report limitation section
- UI wording review
- manual QA notes
```

这些贡献可以有 PR，也可以先以 issue comment / markdown 文件形式提交；它们不应该阻塞 P0 mainline。

---

## 8. Handoff comment after each AI session

每次 AI coding session 结束后，在 PR 或 issue 里留下 handoff：

```md
## Handoff
Completed:
- ...

Tested:
- ...

Not done:
- ...

Risks / questions:
- ...

Next recommended step:
- ...
```

这对异步协作很重要。Reviewer 晚上回来时，可以快速判断：

```text
这个 PR 是否能 merge？
是否需要修改？
是否可以继续下一个 issue？
```

---

## 9. Stop conditions

如果出现以下情况，AI coding agent 应停止扩大修改范围，并在 PR/issue 中说明：

```text
- 需要改动多个核心 schema；
- 需要真实 API key 才能继续；
- DEMO_MODE 被破坏；
- safety behavior 不确定；
- prompt 可能引入医疗建议或情感依赖；
- 需要重构超过当前 issue 范围的大量文件；
- 当前 PR 依赖另一个未合并 PR。
```

---

## 10. Current practical recommendation

当前最现实的开工方式：

```text
Main Completer:
  按 Slice 1 → Slice 2 → Slice 3 顺序连续推进。

Reviewer:
  每天晚上集中审查当天 PR，优先看 demo 行为、安全边界和 scope。

Others:
  暂不强制分工。后续可根据实际在线情况参与 non-blocking docs/QA/test PR。
```

核心目标：

```text
少并发，强主线；
先可运行，再变复杂；
先文本闭环，再语音；
先 mock，再真实 provider；
先安全边界，再功能扩展。
```
