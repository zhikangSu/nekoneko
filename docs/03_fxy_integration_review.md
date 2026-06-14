# fxy 队友稿整合评审与修改记录

版本：v0.4
日期：2026-06-14
对象：`7dfd7d3a-9aef-49db-81e4-67c6bc348d54.md`
输出：已整合进 Overview、PRD、Technical Roadmap，所有新增/改写内容用 `【fxy】` 标注。

---

## 1. 总体判断

队友稿的方向是合理的，尤其是把项目从“功能 demo”提升为“可被 HCI 评估的 research prototype”。其中最值得吸收的是：

- 明确 RQ1–RQ3：可解释性 / 控制感、主动关怀适恰性、可控记忆与信任；
- 双模式对话，但不预设固定角色姓名；
- 回忆话题引导；
- 更完整的 Sensor Preset；
- 主动关怀频率控制；
- Memory Center 三类记忆；
- 更完整的实验流程、指标和 12 周计划。

但其中有几处需要降级或改写：

- “CHI 论文 + 用户实验数据集”不适合作为 SDSC6002 MVP 承诺，只能作为 stretch / future work；
- “真实 65+ 老年人 10–15 人实验”需要导师许可和伦理确认，不能默认承诺；
- “回忆疗法”应改成“回忆话题引导”，避免医疗/治疗声称；
- “救命直接拨号”不适合 MVP，应改为 emergency contact mock；
- 固定角色姓名和“活泼幽默、表情符号、语速稍快”的设定不完全适合老年场景，应改成用户可命名的默认陪伴角色 + 可选回忆话题模式。

---

## 2. 逐项处理表

| fxy 新增内容 | 合理性判断 | 处理方式 | 加入文档位置 |
|---|---|---|---|
| V2.0 学术研究版、12 周、CHI 论文 | 方向好，但作为课程交付过重 | 降级为 12 周增强版 / future work | Overview、PRD 2.4、PRD 8、PRD 16、Tech 12 |
| RQ1–RQ3 | 很合理，可增强 proposal | 吸收，并改为课程可评估版本 | PRD 1.4、PRD 13 |
| 多智能体 + 双角色 + 专职 Agent | 部分合理 | 双角色改为 P1 双模式，不影响 P0 | PRD P9、FR-15、Tech 3.3、Demo 7 |
| 小友 / 老张 | 有启发，但不应内设固定姓名 | 改为用户可命名的默认稳定陪伴 persona + 可选回忆话题模式 | PRD P9、Tech Dialogue Mode |
| 回忆疗法 | 有启发，但“疗法”有医疗暗示 | 改称“回忆话题引导” | PRD P9、FR-15、Tech Workflow |
| Voice I/O 插话、反馈词、重播 | 合理 | P0 保留重播，P1 加 VAD/打断/反馈词 | PRD FR-01、FR-10、Tech 3.0 |
| 6 个 Sensor Preset | 合理 | 吸收；区分传感器 preset 与安全话术 script | PRD FR-06、Tech 9 |
| 主动关怀频率控制 | 非常合理 | 吸收具体规则 | PRD P6、Tech Proactive Policy |
| Memory Center 三类记忆 | 非常合理 | 吸收 | PRD P5、FR-04、Tech Memory Agent |
| 紧急出口直接拨号 | 方向重要，但真实拨号有风险 | 改为 mock emergency contact，不真实拨号 | PRD FR-08、Tech Safety、Risk |
| 真实老人实验 10–15 人 | 研究价值高，但需伦理 | 降级为增强版；MVP 仍 role-play / convenience | PRD 13.6、Tech Research Track |
| NASA-TLX、SUS、Likert、访谈 | 合理 | 吸收进增强版评估 | PRD 13.6、Tech HCI test |
| 团队 4 人分工 | 合理 | 与原分工合并 | Tech 13 |

---

## 3. 更新后的优先级

### P0 不变

- 语音输入输出；
- 多智能体 trace；
- 情绪陪伴；
- 稳定 persona；
- Memory Agent + Memory Center；
- Reminder Agent；
- Mock Sensor + 主动关怀；
- 受控联网查询；
- Safety Agent。

### P1 新增 / 强化

- 双模式对话：默认陪伴模式 + 回忆话题模式，不预设固定角色姓名【fxy】；
- 回忆话题库【fxy】；
- VAD / TTS 打断 / 反馈词处理【fxy】；
- 评估数据导出【fxy】；
- 更完整的主动关怀频率控制【fxy】。

### Future / Stretch

- 真实 65+ 老年人实验【fxy】；
- CHI / CSCW / IMWUT paper submission【fxy】；
- 真实紧急呼叫联动【fxy】；
- 长期纵向研究【fxy】。

---

## 4. 最终建议

fxy 稿可以作为“学术增强版策划书”，但不建议直接替换原 PRD。正确做法是：

1. 保持原有 PRD / Technical Roadmap 的 P0 范围；
2. 把 fxy 的研究问题、评估设计、Memory Center 分类和频率控制吸收进 P0/P1；
3. 把双角色和回忆话题放入 P1；
4. 把真实老人实验、CHI 论文、真实紧急呼叫联动放入 12 周增强版或 future work；
5. 所有 fxy 来源内容都用 `【fxy】` 标注，便于团队后续讨论取舍。

---

## 6. v0.4 命名权与用户范围更新

后续文档已进一步调整两点：

1. **不再内设固定陪伴角色姓名**。fxy 稿中“小友 / 老张”等角色命名保留为设计启发，但主线方案改为“用户可自定义陪伴 AI 称呼”；未命名时使用“陪伴 AI”或第一人称。
2. **目标用户不再限定为某一类老人**。主线方案面向整体老年群体，不同居住状态、年龄段子群体、技术熟悉度和照护需求都只作为场景变量，而不是用户范围限制。
