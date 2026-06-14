# 参考文件架构：老年人多智能体语音陪伴 AI

版本：v0.4
日期：2026-06-14
用途：作为 GitHub repo 初始化、Claude Code / Codex 开发、团队分工和 milestone 拆解的参考目录结构。

命名说明：系统不内设固定姓名。前端、后端、prompt 和测试均应使用 `companion_display_name` 用户设置；未命名前显示“陪伴 AI / AI Companion”。

---

## 1. 推荐总目录

建议 repo 命名：

```text
elderly-companion-ai/
```

推荐结构：

```text
elderly-companion-ai/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── docs/
│   ├── 00_overview_elderly_companion_ai.md
│   ├── 01_prd_elderly_multi_agent_companion_ai.md
│   ├── 02_technical_roadmap_elderly_multi_agent_companion_ai.md
│   ├── 03_fxy_integration_review.md
│   ├── 04_engagement_agent_optimization_review.md
│   ├── 05_reference_project_structure.md
│   ├── demo_script.md
│   ├── safety_policy.md
│   ├── evaluation_plan.md
│   ├── adr/
│   │   ├── 0001-agent-vs-tool-distinction.md
│   │   ├── 0002-safety-critic-escalation.md
│   │   └── 0003-markdown-first-memory.md
│   └── archive/
│       ├── 00_overview_elderly_companion_ai_v0.1_backup.md
│       ├── 01_prd_elderly_multi_agent_companion_ai_v0.1_backup.md
│       ├── 02_technical_roadmap_elderly_multi_agent_companion_ai_v0.1_backup.md
│       ├── 00_overview_elderly_companion_ai_v0.2_pre_engagement_update.md
│       ├── 01_prd_elderly_multi_agent_companion_ai_v0.2_pre_engagement_update.md
│       └── 02_technical_roadmap_elderly_multi_agent_companion_ai_v0.2_pre_engagement_update.md
│
├── backend/
│   ├── pyproject.toml
│   ├── README.md
│   ├── alembic.ini
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── constants.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── health.py
│   │   │       ├── chat.py
│   │   │       ├── voice.py
│   │   │       ├── memory.py
│   │   │       ├── reminders.py
│   │   │       ├── sensors.py
│   │   │       ├── traces.py
│   │   │       └── evaluation.py
│   │   │
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── coordinator.py
│   │   │   ├── companion.py
│   │   │   ├── guardian.py
│   │   │   └── safety_critic.py
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── emotion_classifier.py
│   │   │   ├── memory_tool.py
│   │   │   ├── reminder_tool.py
│   │   │   ├── info_retrieval.py
│   │   │   ├── sensor_simulator.py
│   │   │   ├── input_rule_guard.py
│   │   │   └── output_rule_guard.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── llm_provider.py
│   │   │   ├── fake_llm_provider.py
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   ├── asr_service.py
│   │   │   ├── tts_service.py
│   │   │   ├── weather_service.py
│   │   │   └── clock.py
│   │   │
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── state.py
│   │   │   ├── nodes.py
│   │   │   ├── edges.py
│   │   │   └── build_graph.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── trace.py
│   │   │   ├── memory.py
│   │   │   ├── reminder.py
│   │   │   ├── sensor.py
│   │   │   ├── safety.py
│   │   │   └── evaluation.py
│   │   │
│   │   ├── stores/
│   │   │   ├── __init__.py
│   │   │   ├── db.py
│   │   │   ├── models.py
│   │   │   ├── memory_store.py
│   │   │   ├── reminder_store.py
│   │   │   ├── trace_store.py
│   │   │   └── vector_store.py
│   │   │
│   │   ├── safety/
│   │   │   ├── __init__.py
│   │   │   ├── risk_keywords.py
│   │   │   ├── risk_classifier.py
│   │   │   └── templates/
│   │   │       ├── medical_symptom_zh.md
│   │   │       ├── medication_zh.md
│   │   │       ├── emotional_crisis_zh.md
│   │   │       └── emergency_mock_zh.md
│   │   │
│   │   ├── prompts/
│   │   │   ├── coordinator.md
│   │   │   ├── companion_role_first.md
│   │   │   ├── companion_neutral_assistant.md
│   │   │   ├── guardian.md
│   │   │   ├── safety_critic.md
│   │   │   └── memory_extraction.md
│   │   │
│   │   └── data/
│   │       ├── mock_sensor_presets.json
│   │       ├── topic_bank_zh.json
│   │       └── sample_users.json
│   │
│   ├── migrations/
│   │   └── versions/
│   └── tests/
│       ├── conftest.py
│       ├── test_health.py
│       ├── test_chat_endpoint.py
│       ├── test_trace_schema.py
│       ├── test_coordinator_routing.py
│       ├── test_companion_modes.py
│       ├── test_input_rule_guard.py
│       ├── test_output_rule_guard.py
│       ├── test_safety_critic.py
│       ├── test_guardian_cooldown.py
│       ├── test_memory_store.py
│       ├── test_reminder_store.py
│       ├── test_sensor_presets.py
│       └── test_retrieval_gating.py
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── public/
│   │   └── assets/
│   └── src/
│       ├── app/
│       │   ├── layout.tsx
│       │   ├── page.tsx
│       │   ├── chat/page.tsx
│       │   ├── memory/page.tsx
│       │   ├── reminders/page.tsx
│       │   ├── sensors/page.tsx
│       │   ├── traces/page.tsx
│       │   └── evaluation/page.tsx
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── AppShell.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── Header.tsx
│       │   ├── chat/
│       │   │   ├── ChatWindow.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   ├── VoiceRecorderButton.tsx
│       │   │   ├── ReplayButton.tsx
│       │   │   ├── TranscriptPanel.tsx
│       │   │   ├── ModeToggle.tsx
│       │   │   └── SafetyBanner.tsx
│       │   ├── memory/
│       │   │   ├── MemoryCenter.tsx
│       │   │   ├── MemoryCard.tsx
│       │   │   └── DeleteMemoryDialog.tsx
│       │   ├── reminders/
│       │   │   ├── ReminderList.tsx
│       │   │   ├── ReminderForm.tsx
│       │   │   └── ReminderConfirmation.tsx
│       │   ├── sensors/
│       │   │   ├── SensorSimulator.tsx
│       │   │   ├── SensorPresetButton.tsx
│       │   │   └── SensorSnapshotCard.tsx
│       │   ├── traces/
│       │   │   ├── AgentTracePanel.tsx
│       │   │   ├── TraceStep.tsx
│       │   │   └── AgentToolBadge.tsx
│       │   └── evaluation/
│       │       ├── LikertQuestion.tsx
│       │       ├── TaskChecklist.tsx
│       │       └── ExportDataButton.tsx
│       │
│       ├── hooks/
│       │   ├── useChat.ts
│       │   ├── useVoiceRecorder.ts
│       │   ├── useMemory.ts
│       │   ├── useReminders.ts
│       │   └── useSensorSimulator.ts
│       │
│       ├── lib/
│       │   ├── apiClient.ts
│       │   ├── audio.ts
│       │   ├── constants.ts
│       │   └── formatters.ts
│       │
│       ├── types/
│       │   ├── chat.ts
│       │   ├── trace.ts
│       │   ├── memory.ts
│       │   ├── reminder.ts
│       │   ├── sensor.ts
│       │   └── evaluation.ts
│       │
│       └── styles/
│           └── globals.css
│
├── data/
│   ├── app.db
│   ├── memory/
│   │   └── users/
│   │       └── demo_user/
│   │           ├── profile.md
│   │           ├── preferences.md
│   │           ├── events.md
│   │           └── settings.md
│   ├── traces/
│   └── audio_cache/
│
├── scripts/
│   ├── seed_demo_data.py
│   ├── export_evaluation_data.py
│   ├── reset_demo_db.py
│   └── run_demo_scenario.py
│
└── .github/
    ├── workflows/
    │   ├── backend-tests.yml
    │   └── frontend-tests.yml
    └── ISSUE_TEMPLATE/
        ├── feature.md
        ├── bug.md
        └── demo-scenario.md
```

---

## 2. 主文档如何放置

建议把当前 00–04 主文档放在 `docs/` 根部：

```text
docs/
├── 00_overview_elderly_companion_ai.md
├── 01_prd_elderly_multi_agent_companion_ai.md
├── 02_technical_roadmap_elderly_multi_agent_companion_ai.md
├── 03_fxy_integration_review.md
├── 04_engagement_agent_optimization_review.md
└── 05_reference_project_structure.md
```

含义：

| 文件 | 用途 |
|---|---|
| `00_overview` | 一页式项目索引、定位和阅读顺序。 |
| `01_prd` | 产品需求、MVP、功能优先级、评估设计。 |
| `02_technical_roadmap` | 技术架构、agent/tool 拆分、实现路线。 |
| `03_fxy_integration_review` | 队友 fxy 稿件吸收、降级、拒绝记录。 |
| `04_engagement_agent_optimization_review` | 持续使用意愿、角色优先、福祉优先、真 agent 优化记录。 |
| `05_reference_project_structure` | 本文件，指导 repo 初始化。 |

备份和旧版建议放到：

```text
docs/archive/
```

README 只链接 00–05，不直接链接 archive，避免阅读混乱。

---

## 3. 最小可运行版本目录

如果一开始不想创建完整结构，可以先创建这个最小版本：

```text
elderly-companion-ai/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── .env.example
├── docs/
│   ├── 00_overview_elderly_companion_ai.md
│   ├── 01_prd_elderly_multi_agent_companion_ai.md
│   ├── 02_technical_roadmap_elderly_multi_agent_companion_ai.md
│   ├── 03_fxy_integration_review.md
│   ├── 04_engagement_agent_optimization_review.md
│   └── 05_reference_project_structure.md
├── backend/
│   ├── pyproject.toml
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/chat.py
│   │   ├── agents/coordinator.py
│   │   ├── agents/companion.py
│   │   ├── agents/guardian.py
│   │   ├── agents/safety_critic.py
│   │   ├── tools/input_rule_guard.py
│   │   ├── tools/output_rule_guard.py
│   │   ├── services/fake_llm_provider.py
│   │   └── schemas/trace.py
│   └── tests/
│       ├── test_chat_endpoint.py
│       ├── test_trace_schema.py
│       └── test_input_rule_guard.py
└── frontend/
    ├── package.json
    └── src/
        ├── app/page.tsx
        ├── components/chat/ChatWindow.tsx
        └── components/traces/AgentTracePanel.tsx
```

这个最小目录可以先完成：

```text
文字聊天
+ role_first / neutral_assistant 两种模式
+ input/output guard
+ fake LLM
+ trace panel
```

再逐步加入 Memory、Reminder、Sensor、Guardian、ASR/TTS。

---

## 4. 后端模块说明

### 4.1 `agents/`

只放真正 autonomous agents：

```text
coordinator.py
companion.py
guardian.py
safety_critic.py
```

不要把普通工具放进这里。

### 4.2 `tools/`

放确定性或半确定性的工具逻辑：

```text
emotion_classifier.py
memory_tool.py
reminder_tool.py
info_retrieval.py
sensor_simulator.py
input_rule_guard.py
output_rule_guard.py
```

### 4.3 `services/`

放外部 provider 或可替换服务：

```text
llm_provider.py
fake_llm_provider.py
openai_provider.py
anthropic_provider.py
asr_service.py
tts_service.py
weather_service.py
clock.py
```

所有外部 API 都要有 mock/fake 实现。

### 4.4 `graph/`

放 LangGraph 或状态机实现：

```text
state.py       # graph state schema
nodes.py       # graph node wrappers
edges.py       # conditional routing
build_graph.py # graph construction
```

如果 MVP 暂时不用 LangGraph，也建议保留这个边界，后续迁移更容易。

### 4.5 `schemas/`

放 Pydantic 请求/响应模型：

```text
chat.py
trace.py
memory.py
reminder.py
sensor.py
safety.py
evaluation.py
```

### 4.6 `stores/`

放数据库和持久化：

```text
db.py
models.py
memory_store.py
reminder_store.py
trace_store.py
vector_store.py
```

### 4.7 `prompts/`

提示词必须文件化，便于审查和版本管理：

```text
coordinator.md
companion_role_first.md
companion_neutral_assistant.md
guardian.md
safety_critic.md
memory_extraction.md
```

---

## 5. 前端页面说明

MVP 推荐 5 个核心页面：

```text
/chat       语音/文字聊天主页面
/memory     Memory Center
/reminders  提醒管理
/sensors    Sensor Simulator
/traces     Agent Trace Panel
```

### 5.1 Chat 页面

必须包括：

```text
大号录音按钮
文字输入兜底
用户/陪伴角色消息气泡
transcript
TTS 重播按钮
取消/停止按钮
role_first / neutral_assistant mode toggle
安全提示 banner
```

### 5.2 Memory Center

必须包括：

```text
Profile memory
Event memory
Reminder memory
Consent / settings
删除按钮
暂停记忆按钮
```

### 5.3 Sensor Simulator

必须包括 preset：

```text
Normal Day
Poor Sleep
Low Activity
Medication Missed
Elevated HR Mock
No Response
Low Mood Text Trigger
Medical Risk Script
```

### 5.4 Agent Trace Panel

必须明确区分：

```text
Agent: Coordinator / Companion / Guardian / SafetyCritic
Tool: Memory / Reminder / Retrieval / Sensor / RuleGuard
```

不要在 UI 上把工具全部叫 agent。

---

## 6. API 端点建议

### 6.1 Chat

```http
POST /api/chat
```

Request:

```json
{
  "user_id": "demo_user",
  "message": "今天下午适合出去散步吗？",
  "mode": "role_first",
  "voice_enabled": false,
  "sensor_preset_id": null
}
```

Response:

```json
{
  "turn_id": "t001",
  "response_text": "我帮您看一下今天下午的天气，再结合您平时散步的习惯说说。",
  "audio_url": null,
  "agent_trace": {
    "route": "retrieval_supported_companion_response",
    "agents": [],
    "tools": [],
    "guards": []
  }
}
```

### 6.2 Memory

```http
GET    /api/memory/{user_id}
POST   /api/memory/{user_id}
PATCH  /api/memory/{user_id}/{memory_id}
DELETE /api/memory/{user_id}/{memory_id}
```

### 6.3 Reminders

```http
GET    /api/reminders/{user_id}
POST   /api/reminders/{user_id}
PATCH  /api/reminders/{user_id}/{reminder_id}
DELETE /api/reminders/{user_id}/{reminder_id}
POST   /api/reminders/{user_id}/{reminder_id}/confirm
```

### 6.4 Sensors

```http
GET  /api/sensors/presets
POST /api/sensors/apply-preset
GET  /api/sensors/current/{user_id}
```

### 6.5 Traces

```http
GET /api/traces/{turn_id}
GET /api/traces?user_id=demo_user&limit=20
```

### 6.6 Voice

```http
POST /api/voice/transcribe
POST /api/voice/synthesize
```

Voice endpoints can stay mocked until text pipeline is stable.

---

## 7. 数据目录建议

### 7.1 Markdown memory

```text
data/memory/users/demo_user/profile.md
data/memory/users/demo_user/preferences.md
data/memory/users/demo_user/events.md
data/memory/users/demo_user/settings.md
```

Example `profile.md`:

```md
# Demo User Profile

User display name: 王阿姨
Companion display name: 由用户命名；未命名时为 陪伴 AI
Preferred address: 王阿姨
Preferred language: Mandarin Chinese
Preferred tone: warm, slow, concise

## Stable facts

- Likes Cantonese opera.
- Usually walks in the afternoon.
```

### 7.2 SQLite tables

Recommended tables:

```text
users
memories
memory_audit_logs
reminders
agent_traces
guardian_state
sensor_snapshots
evaluation_sessions
evaluation_responses
```

### 7.3 Trace logs

During demo mode, also write trace JSON to:

```text
data/traces/{turn_id}.json
```

This makes debugging and final report screenshots easier.

---

## 8. `.env.example` 建议

```bash
# Runtime
APP_ENV=development
DEMO_MODE=true
LOG_LEVEL=info

# Providers
LLM_PROVIDER=fake
ASR_PROVIDER=mock
TTS_PROVIDER=mock
RETRIEVAL_PROVIDER=mock

# API keys; leave empty in committed file
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
WEATHER_API_KEY=

# Storage
DATABASE_URL=sqlite:///./data/app.db
MEMORY_ROOT=./data/memory
TRACE_LOG_DIR=./data/traces
AUDIO_CACHE_DIR=./data/audio_cache

# Safety and budget controls
MAX_LLM_CALLS_PER_TURN=2
MAX_WEB_CALLS_PER_TURN=1
SAFETY_CRITIC_ON_LOW_RISK=false
ENABLE_REAL_EMERGENCY_CALL=false

# Proactive defaults
PROACTIVE_ENABLED=true
PROACTIVE_MAX_CHECKINS_PER_DAY=3
PROACTIVE_SAME_TOPIC_COOLDOWN_MINUTES=120
PROACTIVE_REFUSAL_PAUSE_HOURS=24
QUIET_HOURS_START=22:00
QUIET_HOURS_END=07:00
```

---

## 9. GitHub issue 拆分建议

### Milestone 1：项目骨架

```text
#1 Initialize repo with docs, AGENTS.md, CLAUDE.md, README, .env.example
#2 Create FastAPI backend health check
#3 Create Next.js frontend shell
#4 Add Makefile and local dev instructions
```

### Milestone 2：文本聊天核心

```text
#5 Implement FakeLLMProvider
#6 Implement /api/chat endpoint
#7 Implement AgentTrace schema
#8 Implement frontend ChatWindow and transcript
#9 Implement AgentTracePanel
```

### Milestone 3：核心 agents

```text
#10 Implement CoordinatorAgent routing skeleton
#11 Implement CompanionAgent role_first mode
#12 Implement neutral_assistant comparison mode
#13 Implement InputRuleGuard and OutputRuleGuard
#14 Implement SafetyCriticAgent high-risk path
```

### Milestone 4：记忆与提醒

```text
#15 Implement markdown-first MemoryStore
#16 Implement MemoryTool CRUD API
#17 Implement Memory Center UI
#18 Implement ReminderStore and ReminderTool
#19 Implement Reminder UI
```

### Milestone 5：主动关怀

```text
#20 Implement SensorSimulatorTool and presets
#21 Implement GuardianAgent welfare_state
#22 Implement care-vs-restraint decision output
#23 Implement proactive check-in trigger from sensor preset
```

### Milestone 6：受控联网与语音

```text
#24 Implement Retrieval gating logic
#25 Implement mock InfoRetrievalTool
#26 Add optional weather provider
#27 Implement ASR mock endpoint
#28 Implement TTS mock endpoint
#29 Add OpenAI ASR/TTS provider behind config
```

### Milestone 7：Demo 与评估

```text
#30 Implement demo scenarios
#31 Implement evaluation task checklist
#32 Implement Likert form and export
#33 Add safety regression tests
#34 Final demo hardening
```

---

## 10. 推荐开发顺序图

```text
Docs + skeleton
  ↓
Text chat + trace
  ↓
Coordinator + Companion
  ↓
Safety guards
  ↓
Memory Center
  ↓
Reminder
  ↓
Sensor + Guardian
  ↓
Controlled retrieval
  ↓
Voice I/O
  ↓
Evaluation + demo hardening
```

语音不要太早接入。先让文字 pipeline 稳定，再把语音作为 I/O 层接上。

---

## 11. 命名规范

不要在代码中硬编码任何固定陪伴角色名。陪伴 AI 的显示名称应来自用户设置，例如 `companion_display_name`；未命名时使用中性 fallback，例如“陪伴 AI”。


### 11.1 Agents

```text
CoordinatorAgent
CompanionAgent
GuardianAgent
SafetyCriticAgent
```

### 11.2 Tools

```text
EmotionClassifierTool
MemoryTool
ReminderTool
InfoRetrievalTool
SensorSimulatorTool
InputRuleGuard
OutputRuleGuard
```

### 11.3 Modes

```text
role_first
neutral_assistant
reminiscence_mode  # P1 optional
```

### 11.4 Risk levels

```text
low
medium
high
crisis
```

### 11.5 Routes

```text
companion_chat
reminder_management
memory_management
proactive_checkin
retrieval_supported_response
safety_response
emergency_mock
```

---

## 12. 最终建议

项目初始化时不要一次性创建所有文件。建议先创建“最小可运行版本目录”，完成文字聊天、trace、user-named role-first persona 和 safety guard；等核心闭环稳定后，再补齐 Memory、Reminder、Guardian、ASR/TTS 和评估模块。

这个项目的工程风险不在“代码写不出来”，而在范围膨胀和安全边界模糊。目录结构应该帮助团队保持三件事清楚：

```text
什么是真 agent，什么只是 tool；
什么是 P0，什么是 P1 / Future；
什么可以 demo，什么不能声称真实医疗能力。
```
