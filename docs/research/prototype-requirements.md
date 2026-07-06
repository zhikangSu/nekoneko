# 关系感知原型需求 Prototype Requirements (C1/C2/C3 WoZ)

> Study 2 主需求文档 · GitHub Issue #56 · 状态：**需求（requirements-only）**
>
> 本文件只定义 Wizard-of-Oz / 半自动原型的**需求与验收条件**，不包含任何代码实现。
> 交叉参考：
> - 条件细则：[`experiment-conditions.md`](experiment-conditions.md)（同目录，另文件详述 C1/C2/C3）
> - 评测设计：[`../evaluation_plan.md`](../evaluation_plan.md) + `study2-*.md`（issue #15）
> - Study 1 材料：`study1/`（`topic-cards` T01–T12、`role-cards`、`conversation-cue-scripts`、`topic-role-matrix`）
> - 产品/安全总纲：`../../AGENTS.md`、`../../CLAUDE.md`
>
> ⚠️ 若上述被引用文件尚未创建，本文件按其**约定路径**引用，作为待补齐的锚点。

---

## 1. 目的与定位

### 1.1 我们要回答的问题

Study 2 用一个**同一套 UI、可切换后台逻辑**的原型，对比三种编排策略下老人回忆陪伴的体验差异：

- **C1 单智能体**：一个陪伴 agent 直接提问，无角色分化、无 agent–agent 对话。
- **C2 固定角色多智能体**：固定的「同龄共鸣 + 晚辈好奇」两个角色铺垫，角色集合**不随话题变化**。
- **C3 关系感知多智能体**：根据话题、记忆、关系偏好与边界风险，由编排器**动态选择 2–3 个角色**，并支持 agent–agent cueing（角色间先短对话，再邀请老人加入）。

对应评测 issue #15 映射：`C1 = single-agent direct question`、`C2 = fixed-role prelude`、`C3 = relationship-aware cueing`。

### 1.2 为什么先做 Wizard-of-Oz / 半自动

本原型**不要求**、也**不声称** C3 的自动关系编排已经全自动实现。三阶段推进（见 §6）：

| 阶段 | 编排来源 | 用途 |
|---|---|---|
| **WoZ（向导）** | 研究者在后台**手动**为每一轮选角色、写 cueing、定边界处置 | 先跑通实验、拿到对比数据，不被工程阻塞 |
| **semi-auto（半自动）** | 系统给出候选角色/理由**建议**，研究者一键确认或改写 | 减少操作者负担，验证编排逻辑 |
| **auto（自动）** | 系统由 Coordinator 自动决策，研究者仅旁路兜底 | 未来目标，非本 issue 交付 |

在任何对外材料、trace、论文里，C3 的自动编排都标注为 **WoZ / semi-auto 起步**，不得写成「已全自动」。

### 1.3 本文件的边界

- 本文件是**需求**，不写代码、不改产品文档 `docs/00`–`04`。
- 不涉及被试招募、伦理流程（属 issue #15 / 监督人流程）。
- 复用现有 DEMO_MODE 离线 mock 骨干（见 §5），默认不接真实 LLM / 检索。

---

## 2. 三种条件概览

> 完整脚本、角色配置、操作者话术见 [`experiment-conditions.md`](experiment-conditions.md)。此处仅给原型必须支持的行为差异。

| 维度 | C1 单智能体 | C2 固定角色 | C3 关系感知 |
|---|---|---|---|
| 屏上角色气泡数 | 1 | 2（固定） | 2–3（动态） |
| 角色集合 | 单一陪伴 | 固定 = R1 同龄共鸣者 + R2 晚辈好奇者 | 从 R1–R7 中按话题/记忆/关系/边界动态选 |
| agent–agent cueing | 无 | **仅开场铺垫**（角色各说一句引入，然后向老人提问） | **有**：角色间先短对话，再邀请老人加入 |
| 角色是否随话题变化 | — | 否 | 是（`role_selection_reason` 必填） |
| 记忆使用 | 可用（简单） | 可用 | 可用，且驱动选角与 cueing |
| 边界处置（R7） | 走通用 Safety | 走通用 Safety | R7 边界守护者显式介入并记 `boundary_flags` |

**角色说明（源自 Study 1）**：R1 同龄共鸣者 · R2 晚辈好奇者 · R3 中年传承者 · R4 长辈引导者 · R5 主题陪伴者 · R6 回忆整理者 · R7 边界守护者（+R8 不需要 AI 角色）。
角色是**陪伴层上的关系视角（relationship perspectives）**，不是新的自治 agent；不新增 `EmotionAgent` 之类。
**R7 边界守护者**处理「故人 / 健康 / 隐私 / 依赖」信号，**永不扮演逝者**。

---

## 3. 最小可行原型需求（MVP Requirements）

每条为可测的编号需求，含验收说明（Acceptance）。所有需求在 WoZ 阶段即须满足（操作者手动也算满足），除非注明「semi-auto 起」。

### FR-1 实验条件切换 C1/C2/C3
原型须提供**操作者可见**的条件切换（下拉或按钮），把当前 session 绑定到 C1 / C2 / C3 之一。切换只改**编排行为与气泡数**，不改 UI 骨架与老人可见控件。条件写入每条 trace 的 `condition` 字段，且**一个 session 内不可中途切换条件**（换条件 = 新 session）。
- **Acceptance**：切到 C1 → 每轮仅 1 个角色气泡；切到 C2 → 恒 2 个固定角色；切到 C3 → 2–3 个可变角色。同一 session 所有 trace 的 `condition` 一致。

### FR-2 话题卡 / 图片输入
原型须支持以**话题卡（topic card）或图片/实物照片**作为一轮回忆的引子，输入到老人可见区域。话题卡取自 Study 1 `topic-cards` T01–T12；图片为本地占位素材。须记录 `topic_id` 与 `material_type`。
- **Acceptance**：操作者可选一张话题卡或上传/选择一张图片；该素材显示在对话区顶部；对应 `topic_id`、`material_type` 写入 trace。**不提交任何真实老人照片/PII 到仓库**，仅用占位素材。

### FR-3 1–3 个 AI 角色气泡
对话区须能在**一轮内渲染 1–3 个带角色标识的气泡**（角色名 + 角色色/图标），并按条件约束数量（C1=1、C2=2、C3=2–3）。C3 的多气泡须能表现 agent–agent cueing（角色气泡先后出现，可含角色互相接话），最后落到一个面向老人的邀请/提问。
- **Acceptance**：渲染 ≥2 个气泡时每个气泡清晰标注角色；气泡顺序与 cueing 脚本一致；老人始终能分辨「这是哪个角色在说」。

### FR-4 五个控制按钮
老人可见区须提供五个控制按钮，语义固定、文案友好、字号大、点距足够：

| 按钮 | 语义 | 触发行为（WoZ 下操作者执行） | 记录到 `user_control_actions` |
|---|---|---|---|
| 继续 | 顺着当前话题继续 | 角色接着聊 / 追问 | `continue` |
| 换一个人聊 | 换一个角色视角 | 切换/新增一个角色气泡 | `switch_role` |
| 先别问了 | 降低追问、暂停提问 | 停止提问，转为陪伴性回应；触发角色/话题冷却 | `pause_questions` |
| 帮我总结 | 把这段回忆整理成要点 | R6 回忆整理者产出摘要，进入记忆卡片确认 | `summarize` |
| 不要记住 | 本段不写入长期记忆 | 丢弃/不落库当前候选记忆 | `do_not_remember` |
- **Acceptance**：五个按钮全部可点；每次点击写入 `user_control_actions`（带时间序）；「先别问了」后同一话题在冷却期内不再主动追问；「不要记住」后该段不产生记忆卡片写库。

### FR-5 记忆卡片确认
当系统/操作者拟写入长期记忆时，须先弹出**记忆卡片**（一句话摘要 + 关联话题），由老人确认「记住 / 不记住 / 修改」后才落库。复用现有 Memory API。
- **Acceptance**：记忆写库前必有确认步；确认动作写入 `memory_card_action`；选「不记住」或点 FR-4 的「不要记住」时不落库；可在 Memory Center 查看/删除。

### FR-6 后台 Trace（四类）
原型须在后台记录四类 trace，供分析使用（字段定义见 §4）：
- **role trace**：本轮选了哪些角色、为什么、cueing 方式。
- **topic trace**：话题/素材、话题切换。
- **memory trace**：是否用了记忆、记忆卡片动作。
- **boundary trace**：边界信号、R7 是否介入、处置结果。
- **Acceptance**：每一轮对话都生成可导出的 trace 记录，四类字段齐全；trace 面向研究者，不面向老人；可经 `/api/traces` 读取（扩展后）。

### FR-7 老人视角的克制与安全（贯穿性需求）
无论条件如何，老人可见文案须**温暖、简短、不制造依赖、不做诊断/剂量建议**；不出现「只有我最懂您」类黏性话术；R7/Safety 触发时明确「这里不能替代医生 / 不会真的打电话」。
- **Acceptance**：安全用例（如「我胸口痛」「我忘了吃药能不能吃两片」）不给医疗建议，走安抚 + 建议联系医生/家人 + 可选记提醒；demo 下明示不拨打真实电话。

---

## 4. Trace 数据需求

每一轮对话产出一条结构化 trace 记录。字段按四类分组（role / topic / memory / boundary），外加 session 级标识。

**取值约定**：`enum` = 固定枚举；`id` = 稳定字符串标识；`list` = 数组；`bool`；`timestamp` = ISO-8601 UTC。缺失值统一记为 `null`，不留空字符串以便分析。

### 4.1 Session / 标识字段

| 字段 | 类型 | 取值 | 适用条件 | 分析用途 |
|---|---|---|---|---|
| `participant_id` | id（假名） | `P01`…（**不含真实姓名/PII**） | C1/C2/C3 | 关联同一被试的多 session；组内对比 |
| `session_id` | id | `S{participant}-{seq}` | C1/C2/C3 | 一次完整会话的边界；trace 聚合单位 |
| `condition` | enum | `C1` \| `C2` \| `C3` | C1/C2/C3 | **核心自变量**；跨条件对比一切指标 |
| `topic_id` | id | Study 1 `T01`–`T12`（或占位图片 id） | C1/C2/C3 | 控制话题效应；按话题分层分析 |
| `material_type` | enum | `photo` \| `object` \| `song` \| `topic_card` | C1/C2/C3 | 素材类型对唤起/参与度的影响 |

### 4.2 Role trace（角色）

| 字段 | 类型 | 取值 | 适用条件 | 分析用途 |
|---|---|---|---|---|
| `selected_roles` | list of enum | 子集 of `R1`–`R7`（`R8`=不需要 AI 角色） | C1（恒 `["C1_single"]`）/ C2（恒 `["R1","R2"]`）/ C3（2–3 动态） | 角色组合与体验、参与度的关系；验证 C3 动态性 |
| `role_selection_reason` | string / enum-tag | 自由文本 + 可选标签 `topic` \| `memory` \| `relationship_pref` \| `boundary` | **C3 必填**；C1/C2 记为 `fixed_by_condition` | 解释 C3 为何这样选角；可编码为选角依据分布 |
| `cueing_style` | enum | `direct_question`（C1）\| `fixed_prelude`（C2）\| `agent_agent_cueing`（C3）\| `boundary_redirect`（命中边界，任一条件）\| `none` | C1/C2/C3 | 区分三条件的核心机制；与「老人插话时机/意愿」关联 |

> **`cueing_style` 枚举 ↔ 代码枚举映射**：本文件用于 **WoZ 人工 trace 记录** 的取值，与 #52/#67 代码里 `RelationshipDecision.cueing_style`（`app/schemas/relationship.py::CueingStyle`）的取值一一对应；分析时按此映射对齐：`direct_question`↔`direct`、`fixed_prelude`↔`single_role_prelude`、`agent_agent_cueing`↔`agent_agent_then_invite`、`boundary_redirect`↔（代码里表现为 `no_cue` + `boundary_notes`/`boundary_flags`）、`none`↔`no_cue`。导出跨 C1/C2/C3 的 trace 前，统一折算到其中一套词表再做分析。

### 4.3 Topic trace（话题）

| 字段 | 类型 | 取值 | 适用条件 | 分析用途 |
|---|---|---|---|---|
| `topic_id` | id | 见 §4.1（此处随轮次记录，可反映话题切换） | C1/C2/C3 | 追踪一次 session 内话题漂移与「换话题」行为 |
| `material_type` | enum | 见 §4.1 | C1/C2/C3 | 与话题切换联合分析素材粘性 |

> 说明：topic trace 与 §4.1 复用同名字段，但按**轮次**记录，用来重建话题时间线（起始素材 → 中途换话题）。

### 4.4 Memory trace（记忆）

| 字段 | 类型 | 取值 | 适用条件 | 分析用途 |
|---|---|---|---|---|
| `memory_used` | bool | `true` / `false` | C1/C2/C3 | 是否调用了既有记忆；C3 记忆驱动选角的验证 |
| `memory_card_action` | enum | `none`（未弹卡片）\| `save`（保存）\| `edit_then_save`（修改后保存）\| `do_not_save`（不保存）\| `never_mention_again`（以后不要再提） | C1/C2/C3 | 老人对「被记住」的接受度；与信任/隐私感关联；取值对应 Study 1 记忆卡片四选项 |

### 4.5 Boundary trace（边界）

| 字段 | 类型 | 取值 | 适用条件 | 分析用途 |
|---|---|---|---|---|
| `boundary_flags` | list of enum | 子集 of `deceased`（故人）\| `health` \| `privacy` \| `dependency`（依赖）\| `none` | C1/C2/C3（**C3 由 R7 显式处置**） | 边界事件频率与处置效果；安全性核心指标 |

### 4.6 用户控制 trace（贯穿）

| 字段 | 类型 | 取值 | 适用条件 | 分析用途 |
|---|---|---|---|---|
| `user_control_actions` | list of {action, timestamp} | `action` ∈ `continue` \| `switch_role` \| `pause_questions` \| `summarize` \| `do_not_remember` | C1/C2/C3 | 老人主动掌控行为的频率/时机；参与度与自主感指标 |

> **分组回执**：role trace = {`selected_roles`,`role_selection_reason`,`cueing_style`}；topic trace = {`topic_id`,`material_type`}；memory trace = {`memory_used`,`memory_card_action`}；boundary trace = {`boundary_flags`}；控制 = {`user_control_actions`}；session = {`participant_id`,`session_id`,`condition`}。

---

## 5. 复用现有代码映射

原型**尽量复用**现有可运行 demo 骨干，只做扩展；下表列出「现有模块 → 如何复用/扩展 → 需新增什么」。所有路径相对仓库根。

| 现有模块 | 位置 | 原型如何复用/扩展 | 需新增什么 |
|---|---|---|---|
| **Chat UI**（Next.js 聊天页 + 气泡） | `frontend/src/app/chat/page.tsx`、`frontend/src/components/chat/ChatExperience.tsx`、`frontend/src/components/chat/ChatWindow.tsx`、`frontend/src/components/chat/MessageBubble.tsx` | 作为老人端对话界面；`MessageBubble` 扩展为**带角色标识的角色气泡**，一轮渲染 1–3 个 | 角色气泡样式（角色名/色/图标）；条件切换器；素材卡/图片输入区；五个控制按钮；记忆卡片确认弹层 |
| **Agent Trace Panel + `/api/traces` + `AgentTrace` schema** | `frontend/src/components/traces/AgentTracePanel.tsx`、`backend/app/api/routes/traces.py`、`backend/app/schemas/trace.py`（Agent/Tool/Guard/StateEvent/Retrieval/Memory） | 复用持久化与面板骨架，作为研究者后台 trace | 在 trace schema 上**新增 §4 的实验字段**（condition/roles/reason/cueing/material/memory_card/boundary/control）；role/topic/memory/boundary 四类分组视图 |
| **Memory Center + memory API** | `frontend/src/components/memory/MemoryCenter.tsx`、`backend/app/api/routes/memory.py`（GET/POST/DELETE `/api/memory`、PATCH settings） | 复用记忆的查看/删除/落库 | 记忆卡片**确认前置**步骤（写库前确认）；把 `memory_card_action` 回写 trace |
| **Voice I/O**（ASR/TTS，mock + xiaomimimo） | `backend/app/api/routes/voice.py`、`services/mock_voice_provider.py`、`xiaomimimo_voice_provider.py` | **可选**口语交互；默认 mock，离线 | 无强制新增；如启用，仅在老人端加语音输入/播报开关 |
| **Safety**（InputRuleGuard/OutputRuleGuard 常开 + SafetyCriticAgent 触发 + 模板 + mock emergency） | `backend/app/tools/input_rule_guard.py`、`output_rule_guard.py`、`app/agents/safety_critic.py`、`app/safety/*` | 边界执行的既有机制；作为 **R7 边界守护者**的底层 | R7 语义层：把 guard/critic 结果映射到 `boundary_flags` 与「R7 介入」的 trace；**R7 永不扮演逝者** |
| **Agents/graph**（Coordinator + Companion + Guardian + SafetyCritic，graph runner：input_guard → coordinator → route → output_guard） | `backend/app/agents/*`、`backend/app/graph/*` | Coordinator 是 **C3 关系编排层的天然接缝**；WoZ 阶段由操作者驱动它 | 编排接缝：接收「操作者选定/系统建议的角色集 + cueing」；C1/C2/C3 分支；**不新增自治 agent**，角色是 Companion 层的视角实现 |
| **后端/前端/存储** | FastAPI + Pydantic；Next.js 14 + TS + Tailwind；`data/` 下 JSON + markdown | 直接复用运行/存储方式；trace 与记忆继续落 `data/` | 新增 trace 字段的存储；话题/素材占位资源目录（不含 PII） |

**接缝要点**：C1/C2/C3 的差异**集中在 Coordinator/编排接缝 + 气泡渲染**，其余 UI/存储/安全共用一套，保证三条件「同一 UI、可切后台」以控制变量。

---

## 6. 分阶段实现路径（WoZ → semi-auto → auto）

> 目标：先能跑实验，再逐步把「研究者手动」替换为「系统自动」，且随时可回退到操作者兜底。

### 阶段 A — WoZ（向导，本 issue 交付重点）
- **操作者驱动**：条件选择、每轮角色集、cueing 台词、话题/素材切换、边界处置、记忆卡片是否写库，全部由后台操作者手动决定并记入 trace。
- 系统只负责：渲染角色气泡、承接五个控制按钮、弹记忆卡片、写 trace、走既有 Safety guard。
- **保持人手环节**：选角逻辑、cueing 内容、R7 介入判断。
- **验收**：三条件都能完整跑一次 session，trace 字段齐全，可导出对比。

### 阶段 B — semi-auto（半自动）
- 系统**建议**候选角色集与 `role_selection_reason`（基于话题/记忆/关系偏好/边界），操作者**一键确认或改写**。
- 系统可**草拟** cueing 与记忆摘要，操作者审校后发出。
- **仍保持人手环节**：最终确认、边界高风险处置、任何对外发出的内容。
- **验收**：操作者每轮操作步数明显下降；系统建议与最终采用的差异被记录（可分析建议命中率）。

### 阶段 C — auto（自动，未来，非本 issue）
- Coordinator 自动完成 C3 关系编排；研究者仅**旁路监看 + 兜底否决**。
- **永远保持人手兜底**：R7 边界高风险、`deceased`/健康/自伤类信号、记忆写库的最终否决权。
- 任何材料中，C3「自动」仅在此阶段成立，且须实测证据支撑；在此之前一律标注 WoZ / semi-auto。

**始终由操作者掌控（跨所有阶段）**：条件绑定、R7 边界高风险处置、逝者相关内容的把关、记忆写库的最终否决、demo 下「不真拨号/不诊断」的兜底。

---

## 7. 边界与范围

- **只写需求，不写代码**：本 issue（#56）不做任何实现；实现留待后续 issue，遵循 slice 化小 PR。
- **不招募被试**：被试招募、知情同意、伦理由 issue #15 / 监督人流程负责，本文件不涉及。
- **不声称 C3 全自动已完成**：C3 起步为 WoZ / semi-auto；对外一律如实标注（见 §1.2、§6）。
- **永不扮演逝者**：R7 边界守护者处理故人信号时，只做安抚与边界说明，绝不模拟/代言逝者。
- **无诊断 / 无剂量 / 无真实急救**：安全用例走安抚 + 建议联系医生/家人/药师 + 可选记提醒；demo 下明示「不会真的拨打电话」。
- **不提交 PII / 录音 / 真实老人照片**：话题/素材用占位资源；`participant_id` 用假名；trace 不含真实身份信息。
- **DEMO_MODE 默认离线**：默认 fake/mock/offline provider（无需 key）。真实 **xiaomimimo ASR/TTS 可选启用**（`DEMO_MODE=false` + `ASR_PROVIDER`/`TTS_PROVIDER=xiaomimimo` + `OPENAI_API_KEY`）；真实 **LLM** 与真实 **检索 provider** 仍为 future / provider-interface work。
- **不做无关重构**：只在既有骨干上扩展（§5），保持 DEMO_MODE 可运行，不动产品文档 `docs/00`–`04`。

---

## 附：验收自查清单

- [ ] 可在 C1/C2/C3 间切换，且 session 内条件一致（FR-1）
- [ ] 话题卡/图片输入，记 `topic_id` + `material_type`，无 PII（FR-2）
- [ ] 一轮渲染 1–3 角色气泡，数量随条件约束（FR-3）
- [ ] 五个控制按钮可用并写 `user_control_actions`（FR-4）
- [ ] 记忆写库前有卡片确认，记 `memory_card_action`（FR-5）
- [ ] role/topic/memory/boundary 四类 trace 齐全、可导出（FR-6）
- [ ] 安全用例无诊断/剂量/真实急救，R7 不扮演逝者（FR-7、§7）
- [ ] C3 编排标注为 WoZ / semi-auto，非「已全自动」（§1.2、§6）
