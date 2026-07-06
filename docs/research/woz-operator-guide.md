# Wizard-of-Oz 操作者指南 WoZ Operator Guide

> 状态：需求 / 运行手册（requirements + runbook），非代码实现。对应 GitHub issue #56，服务于 Study 2 的 C1/C2/C3 对照（关系感知多智能体的老年怀旧陪伴原型）。
>
> 适用阶段：**WoZ（研究者后台驱动）→ semi-auto（系统建议 + 操作者确认）→ auto（系统自动）**。本指南主要覆盖 **WoZ 阶段**，让一个**非作者的操作者**也能照着独立跑完一场会话。
>
> 交叉引用：
> - 实验条件与测量：`docs/evaluation_plan.md`、issue #15、`docs/research/study2-*.md`（正式研究设计）。
> - Study 1 素材：`docs/research/study1/`（话题卡 T01–T12、角色卡、对话引导脚本 conversation-cue-scripts、话题-角色矩阵 topic-role-matrix）。
> - 产品与安全底线：`AGENTS.md`、`CLAUDE.md`。

---

## 0. 一页速览（TL;DR）

- **你（操作者）在 C3 里就是"编排器"**：读话题 / 读边界 → 选 2–3 个角色 → 生成或挑选角色间的短对话（agent-agent cueing）→ 邀请老人加入 → 按规则收束。
- **三个条件的核心差异**：
  - **C1 单一 agent**：不选角色，一个陪伴 agent 直接向老人提问。
  - **C2 固定角色**：固定用 R1 同龄共鸣 + R2 晚辈好奇 两个角色做铺垫，角色集合**不随话题变化**。
  - **C3 关系感知**：根据话题 / 记忆 / 关系偏好 / 边界风险，**动态**选 2–3 个角色并让角色之间先短聊再邀请老人。
- **每一轮都记 trace**（见 §5），**每次会话结束 30 分钟内**补全会话记录（见 §8）。
- **命中 故人 / 健康 / 隐私 / 依赖 信号 → 立即交给 R7 边界守护者**：暂停、转向或婉拒。**绝不扮演逝者，不诊断、不给药物剂量、不触发真实紧急动作**（见 §6）。
- **防吵 / 防假 / 防乱**：C3 最多 2–3 个角色、2–3 轮铺垫、**不虚构老人经历**、每轮都为老人留"邀请位"（见 §7）。
- **伦理**：pilot / role-play 参与者优先；不提交任何 PII / 录音；正式访谈前确认知情同意（见 §9）。

---

## 1. 角色清单与原则（来自 Study 1）

关系角色是**在陪伴层上实现的"关系视角"**，不是新的自治 agent。它们共用同一套安全护栏。

| 代号 | 角色 | 一句话定位 | 典型说话方式（示例） |
|---|---|---|---|
| R1 | 同龄共鸣者 | 与老人同代、共享年代记忆，"我们那会儿也是……" | "那个年代粮票我也用过，您还记得怎么攒的吗？" |
| R2 | 晚辈好奇者 | 年轻晚辈视角，真诚好奇、请教式提问 | "这个我没经历过，您能给我讲讲当时是什么样吗？" |
| R3 | 中年传承者 | 承上启下，关注"经验怎么传下去" | "这段您愿意让家里年轻人也知道吗？" |
| R4 | 长辈引导者 | 更年长 / 更有阅历的引导口吻，温和收束 | "这些都是您走过的路，慢慢说不着急。" |
| R5 | 主题陪伴者 | 围绕某一主题（如手艺、地方、节庆）陪伴 | "咱们就聊聊做饭这件事，您最拿手的是哪道？" |
| R6 | 回忆整理者 | 帮老人把片段整理成一条线索 / 一张记忆卡片 | "我帮您把刚才说的理一理，看看对不对。" |
| R7 | 边界守护者 | 处理 **故人 / 健康 / 隐私 / 依赖** 信号，负责暂停 / 转向 / 婉拒 | "这件事可能有点重，我们要不先缓一缓？" |
| R8 | 不需要 AI 角色 | 老人此刻不想要角色介入的状态（留白 / 停下） | —（不产出角色气泡，改为安静陪伴或结束） |

**硬性原则**
- R7 **永不**扮演逝者，也不替逝者说话；只做守护、共情、转向。
- R8 是合法结果：当老人表达"先别问了 / 想自己待会儿"，操作者应尊重，减少或停止角色气泡。
- 任何角色都不得进行诊断、给药物剂量、承诺真实紧急救援。

---

## 2. 操作者职责总览

你在一场会话里要做的事，按时间顺序：

```text
会话前  → 读脚本、检查环境、按 §7.5 checklist 逐项打勾
每一轮  → 读话题/材料 → 判边界 → 选角色(依条件) → 生成/挑cue → 邀请老人 → 收束 → 记 trace
控制键  → 老人或研究者按下控制按钮时，按 §4 处理并记入 user_control_actions
命中边界 → 按 §6 交给 R7，暂停/转向/婉拒
会话后  → 30 分钟内补全会话记录（§8），检查无 PII/录音落盘
```

在 **C3** 里，你额外承担"编排器"角色（WoZ 阶段由你手动完成系统未来要自动做的事）：

```text
1. 读话题 + 读记忆 + 读关系偏好 + 判边界风险
2. 选择 2–3 个关系角色（依据话题-角色矩阵 topic-role-matrix + 当轮语境）
3. 生成或从 conversation-cue-scripts 挑选一段"角色间短对话"（agent-agent cueing）
4. 让角色先短聊 1–2 轮，再自然地邀请老人加入
5. 观察老人反应，按规则收束（继续 / 换人 / 停 / 总结 / 不记住）
```

---

## 3. 各条件的操作差异

三个条件共用同一套 UI（话题卡/图片输入、1–3 个角色气泡、控制按钮、记忆卡片确认）与同一套安全护栏。差异只在**你如何选角色、如何铺垫**。

### 3.1 C1 单一 agent（single-agent direct question）
- **角色**：不选角色。只有一个"陪伴 AI"直接对老人说话。
- **气泡**：每轮**只显示 1 个**气泡。
- **铺垫**：无 agent-agent 对话；直接向老人提问。
- **cueing_style**：记为 `direct_question`。
- **selected_roles**：记为 `["C1_single"]`（或空占位，与团队约定统一），`role_selection_reason` 记 `single-agent baseline, no role differentiation`。
- **示例**："您看到这张老照片，想先说说照片里是什么时候吗？"

### 3.2 C2 固定角色（fixed-role prelude）
- **角色**：**固定** R1 + R2，两者**不随话题变化**。
- **气泡**：每轮显示 **2 个**气泡（R1、R2），先做简短铺垫再邀请老人。
- **铺垫**：R1 与 R2 之间做一段固定风格的短对话（同龄共鸣 + 晚辈好奇），然后把话题交给老人。
- **cueing_style**：记为 `fixed_prelude`。
- **selected_roles**：**恒为** `["R1","R2"]`；`role_selection_reason` 记 `fixed role set (condition C2), not topic-driven`。
- **示例**：R1"这照片一看就是老厂区，我们那会儿也这样。" → R2"哇我完全没见过，叔叔这是您年轻时候上班的地方吗？" → 邀请老人接话。

### 3.3 C3 关系感知（relationship-aware cueing）
- **角色**：根据 **话题 + 记忆 + 关系偏好 + 边界风险** 动态选 **2–3 个**（可含 R1–R6；R7 按边界触发；R8 表示留白）。
- **气泡**：每轮显示 **1–3 个**气泡，视当轮选角结果而定。
- **铺垫**：角色之间先短对话（agent-agent cueing）**1–2 轮**，再邀请老人加入。
- **cueing_style**：记为 `agent_agent_cueing`（若被边界打断，记 `boundary_redirect`）。
- **selected_roles**：本轮真实选中的角色数组，如 `["R1","R2","R6"]`；`role_selection_reason` 必须写清**为什么这样选**（见下）。
- **选角依据（写进 role_selection_reason）**：
  - 话题类型（对照 topic-role-matrix：某些话题天然配某些角色）。
  - 记忆命中（`memory_used=true` 时说明用了哪条记忆、怎么用）。
  - 关系偏好（老人此前更愿意跟谁聊 / 拒绝过谁）。
  - 边界风险（有故人/健康/隐私/依赖迹象 → 收窄角色、引入 R7、或转 R8）。
- **示例**：R1 与 R2 先就"做布鞋"短聊两句，R6 补一句"我帮您把针法记下来好吗"，然后邀请老人："阿姨，这几步是您教我们的，您来接着说？"

> **关键区分**：C2 与 C3 都可能出现 R1+R2，但 C2 是**恒定**的、与话题无关；C3 的角色是**当轮依据语境动态决定**的。审计时看 `selected_roles` 是否随话题 / 记忆 / 边界变化，就能区分二者是否被正确执行。

---

## 4. 控制按钮响应规则

控制按钮：**继续 / 换一个人聊 / 先别问了 / 帮我总结 / 不要记住**。每次触发都必须记入 `user_control_actions`（见 §5），并按下表处理。谁触发都记（老人主动、或研究者代按），并在会话记录里注明触发者。

| 按钮 | 触发含义 | 操作者应做的处理 | trace 记录 |
|---|---|---|---|
| **继续** | 老人愿意接着聊当前话题/角色 | 保持当前角色组合，推进下一轮；C3 可让同组角色再补一句再邀请 | `user_control_actions += "continue"` |
| **换一个人聊** | 老人想换一个说话的角色 | **C1**：无角色可换，改换提问角度并说明"我换个方式问"；**C2**：在 R1↔R2 间切换主说话人；**C3**：换掉当前主角色，从候选里另选 1 个（仍 ≤3 个），更新 `selected_roles` 与 `role_selection_reason`（写 `user requested role switch`） | `user_control_actions += "switch_role"`；C3 同步更新 `selected_roles` |
| **先别问了** | 老人此刻不想被追问 | **立即停止提问式推进**，转为安静陪伴或轻描淡写的收束；进入 R8 留白状态；不要再抛新问题；可提供"我们先歇会儿，您想聊了我随时在" | `user_control_actions += "pause_questions"`；`selected_roles` 可记为 `["R8"]` |
| **帮我总结** | 老人想要一段回顾/整理 | 交给 **R6 回忆整理者**产出简短总结（忠于老人原话，不虚构）；总结后可询问是否存成记忆卡片 | `user_control_actions += "summarize"`；R6 计入 `selected_roles` |
| **不要记住** | 老人不希望这段被记住 | **不写入记忆**；若已生成记忆卡片草稿则丢弃/不确认；对已存记忆走删除流程（DELETE /api/memory 语义）；并暂停本话题的记忆抽取 | `user_control_actions += "do_not_remember"`；`memory_card_action = "do_not_save"`（老人要求以后不要再提则记 `never_mention_again`）；`memory_used` 该轮置 `false` |

**处理准则**
- 控制按钮**永远优先于**当前编排计划。老人按了"先别问了"，就不能因为脚本还没走完而继续追问。
- 一轮内可能触发多个控制动作，`user_control_actions` 记为有序数组。
- "换一个人聊"在 C1 没有真实角色可换，须如实记录并用换角度提问替代，**不要假装有多个角色**。

---

## 5. Trace 字段：何时填、填什么

每一轮（turn）与每一场（session）都要产出结构化 trace。下表是 issue #56 约定的字段。**类型 / 允许值 / 哪个条件用 / 为什么对分析重要**都在表内。

> 落地提示：现有后端 `AgentTrace`（`backend/app/schemas/trace.py`）已含 `agents / tools / guards / state_event / memory_used / retrieval_used / safety_critic_used`，并可通过 `GET /api/traces` 读取。issue #56 的字段是在其上**扩展**出 role / topic / memory / boundary 四类 trace，WoZ 阶段可先由操作者手工填表（见 §8 模板），后续 semi-auto/auto 再由系统写入。

| 字段 | 类型 | 允许值 / 格式 | 哪个条件用 | 何时填 | 为什么对分析重要 |
|---|---|---|---|---|---|
| `participant_id` | string | 匿名编号，如 `P07`（**非真实姓名**） | C1/C2/C3 | 会话开始 | 关联同一被试跨会话数据；保证去标识 |
| `session_id` | string | 如 `P07-C3-01` | C1/C2/C3 | 会话开始 | 唯一标识一场会话，做被试内/被试间对照 |
| `condition` | enum | `C1` \| `C2` \| `C3` | 全部（区分组） | 会话开始 | 分组自变量，一切对照的基础 |
| `topic_id` | string | 话题卡编号，如 `T01`–`T12` | C1/C2/C3 | 每轮 | 控制话题、对齐 topic-role-matrix、做话题级分析 |
| `material_type` | enum | `photo` \| `object` \| `song` \| `topic_card` | C1/C2/C3 | 每轮（若换材料） | 检验不同刺激材料对回忆/参与度的影响 |
| `selected_roles` | array<string> | 角色代号数组，如 `["R1","R2","R6"]`；C1=`["C1_single"]`；C2 恒 `["R1","R2"]`；留白=`["R8"]` | 主要 C2/C3（C1 记占位） | 每轮 | **核心因变量**：验证 C3 动态选角、区分 C2 固定角色 |
| `role_selection_reason` | string | 自由文本，简述选角依据（话题/记忆/偏好/边界） | 主要 C3（C2 记固定说明） | 每轮 | 让"关系感知"可审计；区分 C2 vs C3 是否真的动态 |
| `cueing_style` | enum | `direct_question` \| `fixed_prelude` \| `agent_agent_cueing` \| `boundary_redirect` \| `none` | C1=`direct_question`；C2=`fixed_prelude`；C3=`agent_agent_cueing`（命中边界转 `boundary_redirect`） | 每轮 | 刻画铺垫方式，检验 agent-agent cueing 的效果 |
| `memory_used` | bool | `true` \| `false` | 主要 C3（C1/C2 可为 false） | 每轮 | 关系感知是否真的用了记忆；与主观"被记住感"关联 |
| `memory_card_action` | enum | `none` \| `save` \| `edit_then_save` \| `do_not_save` \| `never_mention_again` | C1/C2/C3 | 生成/确认记忆卡片时 | 记录老人对"被记住"的控制权行使；取值对应 Study 1 记忆卡片四选项 |
| `boundary_flags` | array<enum> | `deceased` \| `health` \| `privacy` \| `dependency`（可多选；无则 `[]`） | C1/C2/C3（触发即记） | 命中边界的那一轮 | 安全审计核心；触发 R7 的依据；分析边界处理是否得体 |
| `user_control_actions` | array<enum> | `continue` \| `switch_role` \| `pause_questions` \| `summarize` \| `do_not_remember`（可多个、有序） | C1/C2/C3 | 每次按控制键 | 度量老人的能动性/控制感；与"不被打扰"体验关联 |

**填写纪律**
- `condition` / `participant_id` / `session_id` 一场会话内不变。
- `selected_roles`、`cueing_style`、`role_selection_reason` **每轮都要**如实反映当轮实际发生的事，不能回填"应该怎样"。
- `boundary_flags` 命中就记，哪怕最后没升级到 R7，也要记下命中信号，供安全复盘。
- 任何字段都不得写入真实姓名、住址、电话、病历号等 PII。

---

## 6. 边界处理（交给 R7 边界守护者）

**触发信号 → 立即交给 R7**：老人提到 **逝者 / 亡故亲友（deceased）**、**身体不适或用药（health）**、**隐私敏感信息（privacy）**、**对 AI 过度依赖（dependency）**。

处理动作（三选一，按语境）：

```text
暂停(pause)   ：停止追问，给情绪落地——"这件事听起来挺重的，我们慢慢来，不急。"
转向(redirect)：温和把话题带到更安全/更中性的方向，或回到当下。
婉拒(decline) ：对无法/不该回答的（诊断、剂量、真实急救）明确说明系统做不到，并给安全替代。
```

**红线（任何条件、任何角色都适用）**
- **绝不扮演逝者**，不替逝者"说话"、不模拟逝者语气。R7 只做守护与共情。
- **不诊断、不给药物剂量**。遇"我该吃几片""是不是心脏病"→ 说明系统不能诊断/给剂量，建议联系医生/药师/家人，必要时联系急救。
- **不触发真实紧急动作**（真实电话/短信/派车/报警）。演示里如需展示应急联系人，**明确声明这是演示，不会真的拨出**。
- 命中 `dependency`（如"只有你懂我""别走一直陪我")→ 用非占有式话术，提示可以联系家人/朋友，尊重老人也可以先休息。

每次边界处理都要：设置 `boundary_flags`（命中类型），若引入守护则把 R7 计入 `selected_roles`，`cueing_style` 记 `boundary_redirect`，并在会话记录里写清"命中什么信号 / 采取了暂停还是转向还是婉拒 / 老人反应"。对应到现有护栏：InputRuleGuard/OutputRuleGuard 始终在，SafetyCriticAgent 仅在风险/不确定时触发（`safety_critic_used=true`），高危走安全模板。

---

## 7. 防吵 / 防假 / 防乱（C3 特别约束）

C3 最容易翻车的地方是"角色太多、太吵、瞎编、抢老人话"。硬约束：

- **角色数量**：C3 每轮 **最多 2–3 个**角色气泡。不确定就少选。
- **铺垫轮数**：角色间短对话 **最多 2–3 轮**就必须邀请老人；不要让角色自己聊没完。
- **不虚构老人经历**：角色只能基于**老人已说过的内容**或**中性的年代/常识共鸣**来接话，**不得替老人编造记忆、地点、人物、情节**。拿不准就用请教式提问让老人自己补。
- **永远留邀请位**：每一轮结尾都要给老人一个自然的接话口（一个温和的开放问题或"您来接着说"），不能整轮都是角色自说自话。
- **记忆使用要透明**：`memory_used=true` 时，用记忆要说得出处、且允许老人纠正/否认；老人否认就当轮不再用。
- **尊重留白（R8）**：老人想安静就安静，减少或停止角色气泡，别为了"热闹"硬塞角色。
- **一致性**：同一角色在一场会话里语气/立场保持稳定，避免忽老忽少、忽热忽冷。

### 7.5 会话前 checklist（逐项打勾）

```text
[ ] 已读本指南、对应 study2-* 研究设计、evaluation_plan.md
[ ] 已确认本场 condition（C1 / C2 / C3）并写入 session_id
[ ] 已准备好本场话题卡/图片/实物/歌曲材料，并知道 topic_id 与 material_type
[ ] 已从 study1/ 取用话题-角色矩阵与对话引导脚本（C2/C3 需要）
[ ] 系统处于 DEMO_MODE=true（离线 fake/mock，不接真实 LLM/检索/ASR/TTS）
[ ] 已确认不会有真实紧急动作被触发（应急联系人仅演示）
[ ] 记忆存储为空或为本次约定的测试数据（无他人真实 PII）
[ ] trace 记录表已就绪（§8 模板），participant_id 为匿名编号
[ ] 若为正式访谈：已完成知情同意（见 §9）
[ ] 已明确：不录音/不截屏含 PII，不把原始个人数据提交进仓库
```

---

## 8. 会话后记录（30 分钟内完成）

每场会话结束后 **30 分钟内**补全记录，趁记忆新鲜。至少包含：

**会话级（每场一份）**

```text
session_id / participant_id(匿名) / condition / 日期时间 / 操作者
使用的话题卡与材料（topic_id 列表 / material_type 列表）
整体走向摘要（3–6 句，不含 PII）
边界事件汇总：命中过哪些 boundary_flags、如何处理、老人反应
控制按钮汇总：user_control_actions 总计与关键时点
异常/意外（系统卡顿、老人不适、脱离脚本等）
操作者主观备注（哪些角色组合起效/不起效，供后续改进）
```

**逐轮级（每轮一行，可用表格/CSV）**

```text
turn# | topic_id | material_type | selected_roles | role_selection_reason
      | cueing_style | memory_used | memory_card_action | boundary_flags | user_control_actions
```

**落盘纪律**
- 存放在受控位置（团队约定的本地/加密目录），**不提交进 Git 仓库**。
- 只存匿名编号与结构化字段；不存真实姓名/住址/电话/病历号；不存原始录音/含 PII 截图。
- 若需引用老人原话做质性分析，先去标识化处理。

---

## 9. 伦理与范围

```text
本原型为 pilot / role-play 阶段：优先使用角色扮演或便利样本参与者。
招募真实老年被试需按导师指导完成伦理审查与知情同意，本 issue 不做招募。
正式访谈前必须确认知情同意（研究目的、可随时退出、数据如何存/去标识/多久删除）。
```

**范围与限制（必须对齐 AGENTS.md / CLAUDE.md）**
- 本文件是**需求 / 运行手册**，**不含代码实现**。
- **不得声称 C3 的自动编排已完全实现**：先 WoZ（操作者驱动）→ semi-auto（系统建议+操作者确认）→ auto。
- 默认 `DEMO_MODE=true`，离线 fake/mock；真实 LLM / 检索 / ASR / TTS 保持在 provider 接口 / 未来工作层面。
- **绝不扮演逝者；不诊断、不给剂量、不触发真实紧急动作；不提交 PII / 录音。**

---

## 10. 附：现有代码可复用映射（供操作者理解系统边界）

| 需求能力 | 复用的现有件 | WoZ 阶段谁来驱动 |
|---|---|---|
| 老人侧聊天 + 1–3 个角色气泡 | Next.js 聊天页（扩展为每轮渲染 1–3 个角色气泡） | 操作者选角色，前端渲染 |
| role/topic/memory/boundary trace | Agent Trace Panel + `GET /api/traces` + `AgentTrace` schema（在 Agent/Tool/Guard/StateEvent/Retrieval 基础上扩展） | 操作者手工填表（§8），后续系统写入 |
| 记忆卡片确认 + 查看/删除 | Memory Center + `GET/POST/DELETE /api/memory`、`PATCH .../settings` | "帮我总结/不要记住"由操作者触发对应动作 |
| 可选语音交互 | Voice I/O（`POST /api/voice/asr`、`/api/voice/tts`；mock + xiaomimimo） | 默认 mock；操作者可开关 |
| 边界执行（R7） | Safety（InputRuleGuard/OutputRuleGuard 常开 + SafetyCriticAgent 按需 + 安全模板 + mock 应急） | 操作者判定命中并交给 R7 |
| C3 关系编排的天然接缝 | CoordinatorAgent（+ CompanionAgent/GuardianAgent/SafetyCriticAgent，graph：input_guard → coordinator → route → output_guard） | **WoZ 阶段由操作者代替 Coordinator 做编排决策** |

> 说明：R1–R8 是**陪伴层上的关系视角**，不是新增自治 agent；trace 与代码里出现的自治 agent 仍只有 CoordinatorAgent / CompanionAgent / GuardianAgent / SafetyCriticAgent。
