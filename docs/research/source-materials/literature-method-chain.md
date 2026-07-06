# 关系感知型多智能体老年陪伴系统：下一阶段研究设计

## 0. 当前方向如何继续收敛

后续方向可以继续沿着现有 HTML 的主线走，但把重点压到三个核心机制上：

1. **关系编排**：系统不是固定展示几个 agent，而是根据老人的话题、人生经历、情绪状态、长期记忆和边界需求，动态决定谁说话、谁沉默、谁总结、何时停止。
2. **社会线索引入话题**：不是直接问老人“你想起什么了吗”，而是让两个 agent 先围绕照片、旧物或话题短暂互动，形成一个“多人聊天场”，再邀请老人加入。
3. **多智能体角色交互**：研究不同关系角色之间如何配合，例如同龄共鸣 agent 先建立时代共鸣，晚辈好奇 agent 追问细节，中年传承 agent 总结经验意义，边界守护 agent 在后台判断是否继续。

一句话版本：

> 本研究关注老年虚拟陪伴中“关系角色”如何被动态编排，并验证多智能体之间的短暂互动能否作为社会性记忆线索，更自然地引导老人进入回忆和自我表达。

## 1. 文献支撑应该怎么搭

现在不建议只把文献堆成“多智能体论文综述”，而是按你的三个机制来找支撑。每一类文献都要回答一个问题：它支持了我们为什么要这么做，以及它还没做到什么。

### 1.1 支撑一：老年回忆需要线索、对话和社会情境

这部分支撑“为什么不是普通聊天，而是围绕回忆、照片、旧物和社会互动来设计”。

| 文献方向 | 代表文献 | 能支持什么 | 我们怎么接 |
|---|---|---|---|
| reminiscence / life review | Smart Conversational Agents for Reminiscence | 回忆活动对老年人的心理、社会和情感福祉有价值；技术系统可以支持缺少共同在场人类陪伴的回忆场景 | 把系统目标定位为支持回忆、自我表达和陪伴，而不是普通闲聊 |
| photo-based reminiscence | Understanding and Co-designing Photo-based Reminiscence with Older Adults | 用访谈和共创理解老年人如何使用照片进行回忆，以及他们希望技术如何介入 | 第一阶段也采用半结构访谈 + 共创，用来建立“话题-关系角色”需求矩阵 |
| AI-assisted reminiscence | RemVerse | AI 和动态视觉/对话线索可以帮助老人触发、具体化、深化个人记忆，并提高参与感和自主性 | 我们不做 VR，但借鉴“线索触发 + 对话深化”的逻辑，改成 agent-agent social cue |
| ReminiBuddy / Chorus of the Past | 本地论文和汇总 | older / younger agent 与照片、3D 怀旧物件会影响老年人的回忆体验；年轻 agent 更有情感吸引，年长 agent 更有内容共鸣 | 进一步从固定 older/younger 走向动态关系角色，并把 agent-agent conversation 作为新的记忆线索 |

可以在汇报里这样说：

> 现有老年回忆技术已经说明，照片、旧物、虚拟环境和对话 agent 都能作为记忆线索。但这些研究更多关注“什么线索能触发回忆”，较少研究“谁来引入这个线索、多个 agent 如何共同引入这个话题”。因此我的工作把记忆线索进一步社会化：让 agent 之间先进行短暂互动，再邀请老人加入。

### 1.2 支撑二：多智能体的价值在于编排，而不是数量

这部分支撑“为什么重点是关系编排，不是多个 agent 一起说话”。

| 文献方向 | 代表文献 | 能支持什么 | 我们怎么接 |
|---|---|---|---|
| user control over agents | Perspectra | 用户选择专家 agent、@-mention、thread 和 mind map 能提升批判性思考与方案修改 | 老年陪伴不适合复杂控制，但可以保留低负担控制，如“换同龄人聊”“让晚辈问一句” |
| human orchestration | CrafTeam | 用户一开始期待 agent 自主协作，后来转向由人直接编排 agents | 老人不需要管理复杂 team，但系统应保留方向控制权和轻量选择权 |
| dynamic turn-taking / role participation | YES AND, MultiColleagues | 多 agent 的关键是选择性发言、适时总结和用户介入，而不是所有 agent 抢话 | 我们把“谁说、谁沉默、谁总结”作为关系编排机制的核心变量 |
| debugging / traceability | AGDebugger, DiLLS | 多 agent 系统出错时，需要能查看消息、回滚、诊断 agent 行为 | 实验后台需要记录 role trace、memory trace、topic trace、boundary trace，便于分析为什么系统选择某个 agent |

可以在汇报里这样说：

> 多智能体研究已经从“多个 agent 能不能共同完成任务”转向“人如何选择、理解和编排多个 agent”。我的系统不把老人暴露在复杂 agent 团队前，而是在后台做关系编排，前台只给老人少量、低负担的控制点。

### 1.3 支撑三：agent-agent 互动可以作为社会线索，但要验证

这部分是你最有创新空间的地方。已有多 agent 论文有 agent-agent interaction，但多数用在创意、研究、协作任务里；老年回忆场景中还没有充分验证。

| 已有做法 | 不足 | 我们怎么转化 |
|---|---|---|
| MultiColleagues 让多个职业 agent 互相交流，形成 colleague-like collaboration | 用户是创意任务参与者，不是老年回忆者 | 把“agent 之间先交流”转化为老年人的 social memory cue |
| YES AND 用 confidence-based turn-taking 控制谁发言 | 没有正式用户实验，且场景是 ideation | 借鉴选择性发言，避免多个陪伴 agent 同时抢话 |
| ReminiBuddy 有 older / younger agents，但 responding agents 不真正互相对话 | 缺少 agent-agent conversation 作为记忆线索的实证 | 明确验证“agent-agent short cue 是否比直接提问更能激发回忆” |

可形成一个更清楚的研究 gap：

> Existing multi-agent systems show the value of role diversity and user orchestration, but it remains unclear whether inter-agent conversation can serve as a social memory cue in older-adult reminiscence. This study tests agent-agent conversational cueing as a mechanism for lowering speaking pressure and opening multiple memory entry points.

## 2. 研究问题重新组织

建议现在不要把问题铺太散，先压成一个主问题 + 三个子问题。

### 主问题

> 相比单一陪伴 agent 或固定多角色 agent，关系感知型多智能体编排是否能更好地支持老年人的回忆启动、自我表达、陪伴感、信任感和控制感？

### 子问题

RQ1：**关系编排**

> 老年人在不同话题下希望由哪些关系角色陪伴？系统能否根据话题、记忆和关系偏好动态选择合适 agent？

RQ2：**社会线索引入话题**

> 多个 agent 先进行短暂对话，再邀请老人加入，是否比 agent 直接提问更能降低开口压力、提供更多记忆入口，并增强陪伴感？

RQ3：**多智能体角色交互**

> 不同关系角色如何分工与协作，才能避免信息过载，同时支持共鸣、追问、总结和边界保护？

可作为边界问题的 RQ4：

> 当话题涉及故人、悲伤、隐私或过度依赖风险时，系统应如何解释、暂停、转向或拒绝继续？

## 3. Interview 设计

第一阶段访谈的目标不是证明系统有效，而是建立“老年人关系角色需求”和“话题进入方式”的设计依据。

### 3.1 访谈目的

1. 理解老人平时如何回忆过去，以及和谁聊更自然。
2. 找出不同话题适合哪些关系角色。
3. 理解老人是否接受多个 AI 先聊天再邀请自己加入。
4. 理解哪些记忆可以被系统保存，哪些需要确认或删除。
5. 找出故人、悲伤、隐私、依赖等伦理边界。

### 3.2 参与者

建议：

- 8-12 位 60 岁以上老年人。
- 尽量覆盖不同性别、年龄段、教育背景、职业背景。
- 如果可行，区分独居/非独居、数字技术熟悉/不熟悉。
- 前期不建议纳入严重认知障碍参与者，除非有伦理审批和照护者协助。

### 3.3 访谈结构

建议做 60-90 分钟，分五段。

#### A. 日常回忆习惯

目的：理解老人真实的回忆场景。

问题：

1. 您平时会在什么情况下想起过去的事情？
2. 您一般会和谁聊以前的经历？家人、朋友、同龄人、晚辈、陌生人，还是自己想？
3. 哪些话题您比较愿意讲？哪些话题不太愿意被问？
4. 您更喜欢别人主动问您，还是看到照片/旧物后自己慢慢讲？

#### B. 话题与关系角色匹配

目的：建立“话题-关系角色矩阵”。

可以给老人看一些话题卡：

- 年轻时的学习/工作
- 家庭、孩子、教育经验
- 老朋友、邻居、集体生活
- 人生遗憾、重要选择
- 故人、失去、怀念
- 新技术、新生活方式
- 地方文化、戏曲、老电影、旧物件

问题：

1. 这些话题分别适合和谁聊？
2. 哪些适合同龄人？哪些适合晚辈？哪些适合中年人？哪些适合陌生人或主题人物？
3. 如果 AI 有不同角色，您希望它像谁？不希望它像谁？
4. 您会不会觉得“家人式 AI”尴尬或不真实？

输出：

| 话题 | 更适合的关系角色 | 原因 | 风险 |
|---|---|---|---|
| 工作/奋斗 | 同龄共鸣、中年传承 | 时代共鸣、经验承接 | 追问过深可能疲劳 |
| 家庭/孩子 | 晚辈好奇、中年理解 | 老人愿意传授经验 | 涉及家庭隐私 |
| 故人/失去 | 纪念引导、边界守护 | 温和陪伴、允许停止 | 不能扮演逝者 |

#### C. 社会线索引入话题测试

目的：验证老人是否接受“agent 先聊，再邀请老人加入”。

可以准备 2-3 个微型脚本，让老人比较。

条件 1：直接提问

> AI：看到这个老电视，您想起什么了吗？

条件 2：单 agent 铺垫

> AI：以前电视不只是家里的物件，也常常和邻里、家庭聚在一起有关。您那时候有没有类似经历？

条件 3：两个 agent 先短暂互动

> 同龄 agent：看到这个老电视，我想到以前一家有电视，全院子的人都来看。
> 晚辈 agent：真的会全院子一起看吗？那时候大家是不是还要提前搬凳子？
> 中年 agent：这不只是看电视，也像是邻里关系的一部分。叔叔/阿姨，您那时候有没有类似经历？

访谈问题：

1. 哪种方式让您更想开口？
2. 哪种方式压力更小？
3. 多个 AI 先聊几句会不会自然？会不会吵？
4. 如果 AI 先聊，几句比较合适？
5. 您希望自己什么时候加入？系统要不要明确邀请您？

#### D. 长期记忆与控制

目的：找出什么可以记，怎么记才不冒犯。

问题：

1. 如果系统下次还记得您讲过的故事，您会觉得亲切还是不舒服？
2. 哪些内容可以记？比如职业、兴趣、重要地点、喜欢的话题。
3. 哪些内容需要每次确认？比如家庭关系、身体状况、伤心经历。
4. 哪些内容绝对不希望 AI 记住？
5. 您希望怎样查看、修改或删除这些记忆？

可以展示一个“记忆卡片”概念：

> 今天您提到年轻时做过教师，并且谈到学生考上大学时很骄傲。是否保存？

选项：

- 保存
- 修改
- 不保存
- 以后不要再提

#### E. 边界与伦理

目的：明确故人、悲伤和依赖风险。

问题：

1. 如果聊到已经去世的亲人或朋友，您希望 AI 怎么回应？
2. 您能接受 AI 模仿故人的语气吗？为什么？
3. 如果您讲到难过的事情，AI 应该继续问，还是应该放慢或换话题？
4. 什么情况下您希望系统提醒“这个话题可以先停一下”？

建议设计原则：

> 纪念引导 agent 可以帮助老人讲述与故人有关的记忆，但不扮演逝者本人，不声称自己代表故人，也不诱导老人持续依赖。

## 4. 访谈之后要产出什么

第一阶段不是只写访谈总结，而是要产出能支撑系统设计的中间模型。

### 4.1 角色需求分类

初步可以有：

| 角色需求 | 功能 | 典型话题 |
|---|---|---|
| 共鸣型 | 时代共鸣、共同经历 | 老物件、工作、集体生活 |
| 好奇型 | 追问细节、降低表达门槛 | 照片、家庭故事、旧习俗 |
| 传承型 | 承接经验、总结价值 | 教育子女、职业经验 |
| 引导型 | 人生反思、温和支持 | 遗憾、重要选择 |
| 主题型 | 提供内容共同语言 | 戏曲、地方文化、职业主题 |
| 整理型 | 总结故事、生成记忆卡片 | 对话结束 |
| 边界型 | 识别隐私、悲伤和依赖风险 | 故人、家庭冲突、健康 |

### 4.2 话题-角色匹配矩阵

这个矩阵是后续关系编排的依据：

| 话题 | 首选 agent | 可辅助 agent | 不宜使用 |
|---|---|---|---|
| 老照片/旧物 | 同龄共鸣 | 晚辈好奇、回忆整理 | 强行科普型 |
| 工作经历 | 同龄共鸣 | 中年传承 | 连续追问型 |
| 家庭教育 | 晚辈好奇 | 中年传承 | 评价家庭关系的 agent |
| 故人怀念 | 纪念引导 | 边界守护 | 逝者复刻 |
| 新技术 | 晚辈解释 | 主题桥接 | 与经验无关的新奇推送 |

### 4.3 社会线索设计规则

访谈后要总结：

1. agent 先聊几句最合适？
2. 哪些话题适合 agent-agent cue？
3. 哪些话题不适合多个 agent 先聊？
4. 老人希望如何被邀请加入？
5. 什么时候会觉得吵、假、尴尬？

### 4.4 记忆授权规则

可以分成：

| 记忆类型 | 例子 | 默认处理 |
|---|---|---|
| 事实记忆 | 年轻时做过教师 | 可保存，但需确认 |
| 兴趣记忆 | 喜欢戏曲、老电影 | 可保存，但需可修改 |
| 情感记忆 | 提到学生时很骄傲 | 需谨慎引用 |
| 敏感记忆 | 故人、家庭矛盾、健康 | 默认不保存或强确认 |
| 关系偏好 | 喜欢同龄人，不喜欢连续追问 | 可保存，用于编排 |

## 5. 基于别人怎么做，推出我们怎么做

这是老师可能最想看的逻辑：不是凭空设计，而是从前人方法推导出你的方法。

| 别人怎么做 | 他们解决了什么 | 还没解决什么 | 我们怎么做 |
|---|---|---|---|
| ReminiBuddy 用 older / younger agents + 照片/3D 物件做回忆陪伴 | 证明 agent 身份和 memory cues 会影响老年回忆 | 角色固定；agents 不互相对话；没有 single-agent baseline | 做动态关系编排；验证 agent-agent cue；比较 single / fixed-role / relationship-aware 三条件 |
| Photo-based reminiscence 用访谈 + 共创理解老人如何用照片回忆 | 提供真实日常回忆需求 | 主要围绕照片，不关注多 agent 关系角色 | 第一阶段也做访谈 + 共创，但输出“话题-角色-记忆边界”矩阵 |
| RemVerse 用 AI/VR 线索触发和深化记忆 | 说明动态线索和对话能帮助回忆深化 | 重点是 VR 场景，不是关系角色编排 | 把“动态线索”换成“社会性线索”，由 agent 互动引入话题 |
| Perspectra 让用户选择专家 agent 并组织讨论 | 说明用户控制和结构化多 agent 讨论有价值 | 用户是研究者，不是老年人；控制复杂 | 保留低负担控制，如“换人”“继续”“总结”“不要记住” |
| CrafTeam 发现用户最终倾向 human orchestration | 说明多 agent 不是越自治越好 | 创意任务用户能配置复杂团队，老人不一定能 | 后台自动编排，前台给简单控制点 |
| MultiColleagues / YES AND 强调 turn-taking 和多 agent 互动 | 说明多 agent 的关键是谁该发言和何时总结 | 主要用于创意和问题解决，不是回忆陪伴 | 把 turn-taking 转成陪伴节奏：共鸣、追问、总结、沉默 |
| AGDebugger / DiLLS 强调 trace 和诊断 | 说明多 agent 系统需要可观察性 | 面向开发者，不面向老年用户 | 研究者后台记录 role trace、memory trace、topic trace、boundary trace |

可以形成一个方法链：

> literature review → semi-structured interviews → co-design of role scenarios → relationship-role classification → Wizard-of-Oz prototype → controlled comparison → content coding + experience evaluation

## 6. 我们的方法设计

### Study 1：访谈与共创

目标：

> 建立老年人陪伴关系角色需求、话题-角色匹配矩阵、社会线索接受规则和记忆边界规则。

方法：

- 半结构访谈
- 话题卡排序
- 角色卡匹配
- 三种话题引入方式对比
- 记忆卡片共创

产出：

- 角色需求分类
- 话题-角色矩阵
- agent-agent cueing 设计原则
- 长期记忆授权规则
- 敏感话题边界原则

### Study 2：原型比较

比较三个条件：

| 条件 | 系统形式 | 验证目的 |
|---|---|---|
| C1 Single-agent | 一个陪伴 agent 直接提问 | 基础对照 |
| C2 Fixed-role multi-agent | 固定同龄 + 晚辈 agent | 对照 ReminiBuddy 式固定多角色 |
| C3 Relationship-aware multi-agent | 根据话题和记忆动态选择角色，并支持 agent-agent cueing | 验证关系编排和社会线索机制 |

任务材料：

- 个人照片
- 通用怀旧物件
- 话题卡
- 可选：一段旧歌、地方文化图片、老物件图片

### 评价指标

内容层：

- 自传式记忆数量
- 公共记忆数量
- 具体细节数量：人物、地点、时间、事件、情绪
- 今昔对比
- 自我表达深度：价值判断、遗憾、骄傲、人生总结

体验层：

- 陪伴感
- 社会临场感
- 信任感
- 控制感
- 开口压力
- 认知负担
- 隐私舒适度

行为层：

- 用户说话时长
- 每轮平均回应长度
- 主动补充次数
- 打断次数
- 角色切换次数
- 记忆确认/删除次数
- agent-agent cue 后的回应长度和细节丰富度

## 7. 下一步最应该做什么

优先级建议：

1. **先写文献矩阵**：按“老年回忆线索 / 多 agent 编排 / agent-agent 互动 / 透明与诊断 / 伦理边界”整理。
2. **写访谈提纲**：不要一上来做系统，先问老人到底希望谁来陪、怎么引入话题、哪些内容能被记住。
3. **准备访谈材料**：话题卡、角色卡、三种引入方式脚本、记忆卡片 mockup。
4. **做 Study 1**：8-12 位老人，访谈 + 共创。
5. **根据访谈结果修改 framework**：让关系角色来自用户需求，而不是研究者想象。
6. **再做 Wizard-of-Oz 原型**：验证 agent-agent cueing 和关系编排。

最小可行版本：

> 先不做完整系统，只做 3 个照片/旧物场景 + 3 种话题引入方式，让老人比较哪种更自然、更想讲、更有陪伴感。

## 8. 当前可以跟老师说的版本

> 我想在现有 HTML 的方向上继续收敛，不再泛泛做“多 agent 老年陪伴”，而是聚焦三个机制：关系编排、社会线索引入话题、多智能体角色交互。文献上，我会从老年回忆技术、多 agent 编排、人类控制、多 agent turn-taking 和系统可诊断性几条线来支撑。方法上，第一阶段先做访谈和共创，建立老年人的话题-关系角色需求矩阵；第二阶段再做 Wizard-of-Oz 或半自动原型，比较 single-agent、fixed-role multi-agent 和 relationship-aware multi-agent 三种条件。这样可以从别人已经验证过的“记忆线索、角色差异、用户控制、多 agent 互动”出发，推出我们自己的方法：让 agent-agent conversation 成为社会性记忆线索，并由关系编排机制决定谁来陪、谁说话、何时邀请老人加入。

## 9. 扩展参考文献与用途

文献不需要限制在 10 篇左右。更适合的做法是分成“核心必读”和“扩展支撑”：核心必读直接进入开题汇报和研究设计；扩展支撑用于写 related work、方法论和伦理边界。

### 9.1 核心必读文献

这些文献最直接支撑你的研究问题，建议优先精读并做笔记。

| 类别 | 文献 | 支撑什么 | 对应到我们的做法 |
|---|---|---|---|
| 老年回忆理论 | Butler. **The Life Review: An Interpretation of Reminiscence in the Aged** | life review 不是无意义怀旧，而是老年阶段的重要心理整合过程 | 把系统目标定位为回忆、自我表达、人生意义整理，而不是闲聊 |
| 老年回忆功能 | Webster. **Construction and Validation of the Reminiscence Functions Scale** | 回忆有 conversation、identity、teach/inform、intimacy maintenance 等不同功能 | 访谈中询问老人为什么想讲、讲给谁听、希望获得什么回应 |
| 自传记忆功能 | Bluck & Alea. **A Tale of Three Functions: The Self-Reported Uses of Autobiographical Memory** | 自传记忆服务于自我、社会关系和方向感 | 评价时不只看讲了多少，还看是否出现身份表达、关系连接和经验传承 |
| 回忆干预综述 | Westerhof, Bohlmeijer, Webster. **Reminiscence and Mental Health: A Review of Recent Progress in Theory, Research and Interventions** | 回忆干预和心理健康、适应、意义建构有关 | 作为“为什么做老年回忆支持”的综述依据 |
| 回忆干预效果 | Pinquart & Forstmeier. **Effects of Reminiscence Interventions on Psychosocial Outcomes: A Meta-Analysis** | 回忆干预可影响抑郁、幸福感、生活满意度、自我整合等结果 | 选取体验量表和访谈编码维度 |
| 失智/老年回忆 | Woods et al. **Reminiscence Therapy for Dementia** | 回忆疗法常用照片、旧物、音乐等线索，并关注沟通和生活质量 | 支撑使用照片、旧物、地方文化材料作为回忆入口 |
| 技术支持回忆综述 | Lazar et al. **A Systematic Review of the Use of Technology for Reminiscence Therapy** | 技术可支持回忆，但常面临可用性、个性化和照护情境问题 | 说明我们的系统需要低负担交互和个性化线索 |
| 照片回忆共创 | Zhang et al. **Understanding and Co-designing Photo-based Reminiscence with Older Adults** | 用访谈和共创理解老人如何使用照片回忆 | Study 1 采用访谈、话题卡、角色卡和共创脚本 |
| 对话 agent 回忆 | Nikitina, Callaioli, Baez. **Smart Conversational Agents for Reminiscence** | 对话 agent 可以降低人类陪伴不足的问题，并支持持续回忆活动 | 支撑“AI 陪伴者作为回忆支持工具” |
| AI/VR 回忆线索 | Li et al. **RemVerse: Supporting Reminiscence Activities for Older Adults through AI-Assisted Virtual Reality** | AI 生成的动态线索与对话可以触发、具体化、深化记忆 | 我们把视觉/VR 线索转成“社会性对话线索” |
| 多角色回忆系统 | **Chorus of the Past / ReminiBuddy** | older / younger agents 和照片/3D 物件会影响回忆体验 | 作为最直接 baseline；我们进一步做动态角色编排和 agent-agent cueing |
| 关系型 agent | Bickmore & Picard. **Establishing and Maintaining Long-Term Human-Computer Relationships** | 长期关系建立需要记忆、社交回应和关系维护策略 | 支撑长期信任、持续记忆和关系感知设计 |
| 老年关系型 agent | Bickmore et al. **“It’s Just Like You Talk to a Friend”: Relational Agents for Older Adults** | 老年用户可能把 agent 视为类似朋友的对话对象 | 支撑陪伴感和自然对话，但也提醒边界管理 |
| 老人多话题对话 | Razavi et al. **Discourse Behavior of Older Adults Interacting with a Dialogue Agent Competent in Multiple Topics** | 话题亲密度会影响老人话语量、自我披露和情绪表达 | 访谈和实验中要区分低/中/高亲密话题 |
| 社会性记忆 | Rajaram & Pereira-Pasarin. **Collaborative Memory: Cognitive Research and Theory** | 多人回忆存在 cross-cueing，也可能有 collaborative inhibition | agent-agent cue 不能默认有效，必须比较直接提问和多人线索 |
| 共同记忆风险 | Roediger, Meade, Bergman. **Social Contagion of Memory** | 社会互动可能引入错误记忆 | 设计边界守护和“不编造私人事实”的规则 |
| 对话轮替 | Sacks, Schegloff, Jefferson. **A Simplest Systematics for the Organization of Turn-Taking for Conversation** | 日常对话有 turn allocation、self-selection、current speaker selects next 等机制 | 多 agent 角色交互要设计谁说、谁沉默、谁邀请老人加入 |
| 多 agent 角色社会 | Park et al. **Generative Agents: Interactive Simulacra of Human Behavior** | agent 可以通过记忆、反思和计划形成可信的社会行为 | 后台使用长期记忆和角色状态，但前台保持简单 |
| LLM 多 agent 框架 | Wu et al. **AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation** | 多 agent 对话需要 agent 角色、消息传递和人类介入 | 技术实现上可借鉴 agent conversation 和 human-in-the-loop |
| 多 agent 角色协作 | Li et al. **CAMEL: Communicative Agents for “Mind” Exploration of Large Scale Language Model Society** | 角色扮演式 agent 可以通过对话协作完成任务 | 说明“角色差异”是可设计变量，但我们的场景是陪伴而非任务完成 |
| 多 agent 软件组织 | Hong et al. **MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework** | 通过 SOP 和角色分工组织 agent 协作 | 可借鉴“角色职责清晰化”，但要转成低认知负担陪伴流程 |
| 用户编排 agents | Lim et al. **Understanding Human–Multi-Agent Team Formation for Creative Work / CrafTeam** | 用户会从期待 agent 自主协作转向想要直接编排团队 | 老人前台不配置复杂团队，系统后台自动编排并提供简单控制 |
| 用户选择专家 | Liu et al. **Perspectra: Choosing Your Experts Enhances Critical Thinking in Multi-Agent Research Ideation** | 选择 agent 能提升用户 agency 和思考质量 | 老年场景中转化为低负担选择：“换个人聊”“让晚辈问一句” |
| 多 agent 同事感 | Quan et al. **Towards AI as Colleagues / MultiColleagues** | 多 agent 互动可以形成 colleague-like collaboration 和社会临场感 | 转化为“多人陪伴感”和 agent-agent social cue |
| 轮替机制 | **YES AND: Confidence-Based Agent Turn-Taking** | 选择性发言、点名、总结能避免 all-agents-response 的噪声 | 关系编排中明确“谁该说、谁该沉默、何时总结” |
| 多 agent 可观察性 | Epperson et al. **AGDebugger**; **DiLLS** | 多 agent 系统需要可观察的行为 trace 和诊断机制 | 实验后台记录 role trace、topic trace、memory trace、boundary trace |

### 9.2 扩展支撑文献

这些文献不一定都放进汇报 PPT，但可以用于论文 related work 或开题报告正文。

| 类别 | 文献 | 可以怎么用 |
|---|---|---|
| 回忆类型与干预 | Watt & Cappeliez. **Integrative and Instrumental Reminiscence Therapies for Depression in Older Adults** | 区分“情绪整合型回忆”和“经验/应对型回忆”，帮助设计不同 agent 角色 |
| 生活叙事与身份 | Pasupathi. **The Social Construction of the Personal Past and Its Implications for Adult Development** | 支撑回忆不是单人认知行为，而是在听者回应中被共同建构 |
| 集体回忆 | Weldon & Bellinger. **Collective Memory: Collaborative and Individual Processes in Remembering** | 支撑多人回忆既可能促进线索触发，也可能干扰个人组织 |
| 协作记忆干扰 | Basden et al. **A Comparison of Group and Individual Remembering: Does Collaboration Disrupt Retrieval Strategies?** | 解释为什么 agent-agent cue 必须短、轻、可退出 |
| conversation grounding | Clark & Brennan. **Grounding in Communication** | 支撑 agent 之间要建立共享语境，不能直接抛出孤立问题 |
| conversational repair | Schegloff et al. **The Preference for Self-Correction in the Organization of Repair in Conversation** | 可用于设计老人说错、停顿、否认时 agent 如何修正和接话 |
| 老人自主性 | An. **Autonomy for Older Adult-Agent Interaction** | 支撑老年 agent 交互不能只追求自动化，还要保护决策自主、控制自主和社会责任 |
| 虚拟 agent 空间距离 | Pochwatko et al. **Interpersonal Distance in VR: Reactions of Older Adults to the Presence of a Virtual Agent** | 如果后续有头像/虚拟形象，可作为老年用户舒适距离和社会临场感参考 |
| 自动回忆治疗 | Caros et al. **Automatic Reminiscence Therapy for Dementia** | 支撑“照片自动生成提问”的路线，也说明单 agent 自动提问是一个可比较 baseline |
| 照护者需求 | Alarcao et al. **Developing Assistive Technology to Support Reminiscence Therapy** | 如果研究加入家属/照护者，可支持“记忆材料准备负担”和“负面情绪处理” |
| AI-in-the-loop 回忆工具 | Seah et al. **Rememo** | 支撑生成式 AI 不一定替代人类陪伴，也可以支持照护者/治疗师的关系性工作 |
| AI 链式协作 | Wu et al. **AI Chains: Transparent and Controllable Human-AI Interaction by Chaining Large Language Model Prompts** | 支撑把复杂 LLM 流程拆成可理解、可控制步骤 |
| 人机交互指南 | Amershi et al. **Guidelines for Human-AI Interaction** | 用于解释系统如何告知能力、处理错误、允许用户控制和修正 |
| 信任自动化 | Lee & See. **Trust in Automation: Designing for Appropriate Reliance** | 支撑“信任感”不能越高越好，而是要校准和可控 |
| 信任综述 | Hoff & Bashir. **Trust in Automation: Integrating Empirical Evidence on Factors that Influence Trust** | 用于设计信任、可靠性、可解释性相关问卷和访谈问题 |
| 自动化与人类控制 | Parasuraman & Riley. **Humans and Automation: Use, Misuse, Disuse, Abuse** | 支撑过度依赖与误用风险，连接边界守护 agent |
| LLM 多 agent 软件开发 | Qian et al. **ChatDev: Communicative Agents for Software Development** | 作为多 agent 角色分工的技术背景，不是核心用户研究依据 |
| 早期用户实践 | **Exploring Early Adopters’ Use of AI Driven Multi-Agent Systems** | 支撑真实使用中需要透明、可控和 human oversight |
| 多 agent 透明信任 | **Sensemaking in Multi-Agent LLM Interfaces** | 支撑用户会根据界面线索理解 agent 可信度，不能让多 agent 看起来神秘不可控 |
| 安全角色编排 | Cho. **A Safety-Aware Role-Orchestrated Multi-Agent LLM Framework for Behavioral Health Communication Simulation** | 可作为“边界守护 agent / safety evaluator”的新近技术参考 |
| 人类监督编排 | Zhou. **OrchVis: Hierarchical Multi-Agent Orchestration for Human Oversight** | 可作为后台可视化和研究者监督的扩展方向，不必直接给老人看 |

### 9.3 文献如何转成你的方法

可以把文献贡献压成四条方法来源：

1. **从回忆疗法和自传记忆文献得到研究目标**：不是让老人“多聊天”，而是支持身份连续性、社会连接、经验传承和情绪整合。
2. **从技术支持回忆文献得到材料和访谈方法**：用照片、旧物、地方文化、旧歌和话题卡做半结构访谈与共创。
3. **从社会性记忆和对话分析文献得到核心机制**：agent-agent cueing 的理论依据是 cross-cueing、共同建构和 turn-taking；风险是干扰、过度引导和错误记忆。
4. **从多 agent 和 human-AI interaction 文献得到系统机制**：动态选择角色、限制发言数量、保留用户控制、记录后台 trace，并设置边界守护。

因此，你的方法不是“把很多 agent 放进聊天框”，而是：

> 先用访谈识别老年人的话题-关系角色需求，再把这些需求转化为多智能体编排规则；系统通过少量 agent-agent 对话提供社会性记忆线索，并用边界守护与用户控制避免过度打扰、错误记忆和情感依赖。
