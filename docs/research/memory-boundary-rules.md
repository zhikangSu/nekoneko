# 授权记忆卡规则 / Authorized Memory Card Rules

Issue #54 — implementation-facing rules for the授权记忆卡 (Authorized Memory Card) workflow.

本文件定义**候选记忆如何被识别、分类、呈现给用户，以及用户如何授权其写入长期记忆**。核心原则：记忆**始终可见、可确认、可编辑、可删除**；敏感内容**永不自动保存**；只有在用户**显式操作**后才写入 `MemoryStore`。

分类器为**规则驱动 (rule-based)，不使用 LLM**。

> 与 CLAUDE.md §7 / AGENTS.md 的记忆约束一致：记忆可控、以用户同意为前提、不存储医疗诊断类记忆、不使用故人内容冒充逝者。

---

## 1. 工作流概览

```text
用户话语 (text)
  → 规则分类器 (rule-based, no LLM)
  → 生成 MemoryCard 草稿 (status=pending)   ← 尚未写入任何记忆
  → 前端呈现候选卡：summary + why_save + sensitivity
  → 用户选择四个动作之一
  → apply_action:
       保存 / 修改后保存  → 写入 MemoryStore
       不保存             → 什么都不写
       以后不要再提       → 写入边界偏好 (boundary preference)，而非普通记忆
```

一句话草稿若匹配不到任何候选类型，则**不生成卡片**（API 返回 204）。

---

## 2. 五种候选类型 / Candidate Types

分类器为每条候选话语判定一个 `candidate_type`，并附带 `sensitivity` 与 `default_action`。

| 类型 (`candidate_type`) | 中文 | 触发线索（示例） | `sensitivity` | `default_action` |
| --- | --- | --- | --- | --- |
| `interest` | 兴趣 | “我喜欢 X”、“我爱 X” | `low` | `suggest_save` |
| `fact` | 事实 | “我年轻时做过 X”、“我做过 X”、“我当过 X”、“我是 X”、“我以前是 X”、“我住过 X” | `low` / `medium` | `confirm_before_save` |
| `emotion` | 情感 | 一段经历 + 情绪词（骄傲/难过/开心/遗憾/后悔/想念/自豪） | `medium` | `confirm_before_save` |
| `sensitive` | 敏感 | 老伴去世 / 老伴走了 / 去世 / 生病 / 住院 / 家里矛盾 / 吵架 / 隐私 | `high` | `do_not_save_by_default` |
| `boundary_preference` | 边界偏好 | “我不想再聊 X”、“不想聊 X”、“别再提 X”、“以后别提 X”、“不喜欢聊 X”、“不喜欢某角色” | `medium` | `confirm_before_save`（作为保护性边界也可 `suggest_save`） |

### `default_action` 语义

| `default_action` | 含义 |
| --- | --- |
| `suggest_save` | 系统主动建议保存，用户一键确认即可（默认倾向保存）。 |
| `confirm_before_save` | 呈现草稿但**需要用户明确确认**才写入。 |
| `do_not_save_by_default` | **默认不保存**；仅生成草稿供用户查看，只有在用户**显式点击“保存”**时才写入。用于 `sensitive`。 |

> **关键安全约束**：`sensitive` 内容 `default_action` 恒为 `do_not_save_by_default`，**永不自动保存**。系统只呈现草稿，是否落库完全由用户决定。

### 多类型命中时的优先级 / Priority

同一句话可能命中多个模式。按以下顺序取**第一个**匹配：

```text
1. boundary_preference   (“不想再聊 / 别提 / 以后别提” 这类边界意图最优先)
2. sensitive
3. fact
4. emotion
5. interest
```

因此：

- “我不想再聊老伴去世的事” → `boundary_preference`（**不是** `sensitive`）。
  用户表达的是“别再提”的边界意图，应被当作保护性偏好处理，而不是把敏感往事存下来。

---

## 3. 四个用户动作 / Four User Actions

每张 `pending` 卡片，用户可选四种动作之一。动作 token 与 `apply_action` 语义如下：

| 界面按钮 | action token | 行为 | 结束 `status` |
| --- | --- | --- | --- |
| **保存** | `save` | 将 `summary` 写入长期记忆：`MemoryStore.add(user_id, category, summary)` | `saved` |
| **修改后保存** | `edit_then_save` | 将用户改写后的 `edited_summary` 写入长期记忆 | `edited_saved` |
| **不保存** | `reject` | **什么都不写入记忆**；仅将卡片标记为已拒绝 | `rejected` |
| **以后不要再提** | `never_mention` | 写入一条**边界偏好**（`MemoryCategory.boundary_preference`），内容表述为“回避规则”，**不是普通记忆** | `never_mention` |

### 三条必须记住的语义

1. **不保存 (`reject`) = 一个字都不写。**
   不是“存到别处”、不是“软删除”——记忆库中不产生任何条目，卡片仅记为 `rejected`。

2. **以后不要再提 (`never_mention`) = 存为边界偏好，而非普通记忆。**
   写入 `MemoryCategory.boundary_preference`，内容措辞为**回避规则**，例如：

   ```text
   以后不要再提：<summary>
   ```

   这样系统记住的是“**不要触碰这个话题**”，而不是把原始（可能敏感的）内容当作可回忆的往事保存下来。后续对话据此主动回避该话题。

3. **修改后保存 (`edit_then_save`)** 允许用户在落库前编辑措辞，保证用户对“系统到底记住了什么”拥有最终控制权。

---

## 4. 类别映射 / Category Mapping（save / edit）

当动作为 `save` 或 `edit_then_save` 时，按 `candidate_type` 映射到 `MemoryCategory`：

| `candidate_type` | 写入的 `MemoryCategory` |
| --- | --- |
| `interest` | `profile_preference` |
| `fact` | `event_memory` |
| `emotion` | `event_memory` |
| `boundary_preference` | `boundary_preference` |
| `sensitive` | `event_memory` —— **仅在用户显式 `save` 时**，绝不自动 |

`never_mention` 动作与上表无关：无论原类型是什么，一律写入 `boundary_preference`（回避规则表述）。

> `MemoryCategory` 需新增 `boundary_preference` 取值（原有：`profile_preference` / `event_memory` / `reminder_or_setting`）。

---

## 5. 数据结构 / MemoryCard

```text
MemoryCard
  card_id:         str
  user_id:         str
  candidate_type:  enum(interest | fact | emotion | sensitive | boundary_preference)
  summary:         str
  why_save:        str
  sensitivity:     enum(low | medium | high)
  default_action:  enum(suggest_save | confirm_before_save | do_not_save_by_default)
  source_turn_id:  str | None
  status:          enum(pending | saved | edited_saved | rejected | never_mention)
  created_at:      str
```

`why_save` 是给用户看的“为什么建议记住这条”的简短解释，支撑“可确认”原则。

---

## 6. REST API（前缀 `/api/memory-cards`）

| 方法与路径 | 请求体 | 响应 |
| --- | --- | --- |
| `POST /api/memory-cards/{user_id}/draft` | `{ text: str, source_turn_id?: str }` | `201` MemoryCard，或 `204`（未找到候选） |
| `GET  /api/memory-cards/{user_id}?status=pending` | — | `{ user_id, cards: MemoryCard[] }` |
| `POST /api/memory-cards/{user_id}/{card_id}/action` | `{ action, edited_summary? }` | `200` MemoryCard（已更新） |

- `action` ∈ `save | edit_then_save | reject | never_mention`。
- `edited_summary` 仅在 `edit_then_save` 时需要。
- `draft` 端点**只生成草稿**，不写入记忆；写入只发生在 `action` 端点且动作为 `save` / `edit_then_save` / `never_mention`。

---

## 7. 可控性与安全约束（不可回退的规则）

记忆必须满足以下全部条件——这是 #54 的验收底线：

- **可见 (visible)**：候选记忆以卡片形式呈现，用户能看到 `summary`、`why_save`、`sensitivity`。
- **可确认 (confirmable)**：除显式操作外不写入；`confirm_before_save` / `do_not_save_by_default` 强制用户确认。
- **可编辑 (editable)**：`edit_then_save` 允许改写后再落库。
- **可删除 (deletable)**：已保存条目可经 `MemoryStore.delete` 移除（沿用 #10 记忆中心能力）。
- **敏感内容永不自动保存**：`sensitive` 恒为 `do_not_save_by_default`，只作草稿，仅显式 `save` 才落库。
- **不存储医疗诊断类记忆**：不把“疾病诊断 / 用药结论”写成可回忆记忆（与 CLAUDE.md §9 安全边界一致）。
- **不使用故人 (故人) 内容冒充逝者**：与逝者相关的往事即使被保存，也仅作用户自身的回忆条目，**绝不**用于让 AI 扮演 / 模拟已故者的口吻或身份。
- **仅在显式动作后持久化**：任何自动流程（草稿生成、分类）都不写记忆库；只有用户动作触发写入。

---

## 8. 与 Study-1 记忆卡的关系

本规则文档是 Study-1 概念研究向可实现契约的落地。它承接并对齐由 #50 / #55 引入的研究材料：

- `docs/research/study1/memory-card-examples.md` — Study-1 阶段的记忆卡样例（各候选类型的真实话语与建议保存措辞），本实现的分类线索与 `summary` / `why_save` 表述应与这些样例保持一致。
- `docs/research/study1/memory-boundary-rules.md` — Study-1 阶段的记忆边界原则（可见 / 可控 / 敏感不自动保存 / 边界偏好 / 故人不冒充）。本文件将这些研究原则固化为**面向工程实现的类型、动作、`default_action`、优先级与 API 契约**。

对应关系：Study-1 文档回答“**为什么这样对待老人的记忆**”（伦理与研究依据）；本文件回答“**系统据此如何分类、如何授权、如何落库**”（可执行规则）。两者若出现冲突，以 Study-1 的边界原则为上位约束，实现细节向其收敛。
