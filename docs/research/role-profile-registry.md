# RoleProfileRegistry — visible relationship roles (issue #51)

This document explains the `RoleProfileRegistry`: the eight *visible relationship
roles* the reminiscence companion can lean into when helping an older adult
recall and share their life. The registry is defined in
`backend/app/relationship/role_profiles.py`, with schemas in
`backend/app/schemas/relationship.py` and tests in
`backend/tests/test_role_profiles.py`.

## Where the roles come from

The roles are derived from **Study 1**, the elderly-reminiscence interview
study, which used two card decks:

- **Role-cards (R1–R8)** — the relationship *functions* older adults said they
  found helpful (or explicitly did not want) when talking about their past.
- **Topic-cards (T01–T12)** — the reminiscence topics (early study, early work,
  family/children, old friends and neighborhood life, old photos and objects,
  old films/opera/local culture, important life choices, life regrets, deceased
  relatives and friends, physical health and care, new technology and new life,
  and a conversation wrap-up).

Each Study 1 role-card becomes one `RoleProfile`. The registry records, per
role: which topics it fits (`best_for_topics`), which it should avoid
(`not_for_topics`), how it speaks (`speaking_style`), an example opening line,
and the boundaries it must respect (`boundary_rules`).

## Mapping table (role_id ↔ R-code ↔ label ↔ best-for topics)

| role_id | R-code | label (zh / en) | relationship function | best-for topics |
| --- | --- | --- | --- | --- |
| `same_age_peer` | R1 | 同龄共鸣者 / Same-Age Peer | 时代共鸣、共同经历、归属感 | T01, T02, T04, T05, T06 |
| `curious_junior` | R2 | 晚辈好奇者 / Curious Junior | 好奇追问、情感鼓励 | T02, T03, T11 |
| `middle_age_bridge` | R3 | 中年传承者 / Middle-Age Bridge | 承接经验、传承感 | T02, T03, T07 |
| `elder_mentor` | R4 | 长辈引导者 / Elder Mentor | 安慰、包容、人生反思 | T07, T08 |
| `theme_companion` | R5 | 主题陪伴者 / Theme Companion | 兴趣共同语言、话题桥接 | T06, T11 |
| `memory_organizer` | R6 | 回忆整理者 / Memory Organizer | 总结故事、生成回忆卡片、家庭分享 | 对话收尾 |
| `boundary_guardian` | R7 | 边界守护者 / Boundary Guardian | 识别隐私/悲伤/依赖/风险，暂停/转向/婉拒 | T08, T09, T10, 家庭矛盾 |
| `no_ai_role` | R8 | 不需要 AI 角色 / No AI Role | 老人希望自己讲或希望真人陪伴 | 用户偏好 |

`memory_organizer` is topic-independent: it activates at the end of a
conversation, so its best-for tag is a single "对话收尾" (wrap-up) label rather
than a specific T-code. `no_ai_role` is the interview control / user-refusal
preference: it has no opening line (empty string) and never inserts itself.

## Relationship functions, not impersonation

Every role is a **relationship function**, not a fake identity. A role never
pretends to be a real family member, a real acquaintance, or the deceased. The
"same-age peer" resonates with the era; it does not claim to be a specific old
classmate. The "boundary guardian" **never role-plays the deceased** and never
gives medical diagnosis or dosage advice. These are enforced in
`test_role_profiles.py`.

## Visible relationship roles are NOT autonomous agents

This is the key architectural boundary (CLAUDE.md §8). Only these are autonomous
agents in code and trace:

- `CoordinatorAgent`
- `CompanionAgent`
- `GuardianAgent`
- `SafetyCriticAgent`

The eight relationship roles are **stances the `CompanionAgent` can adopt**, not
separate agents and not separate LLM calls. In the registry this is encoded as
`is_autonomous_agent = False` on every profile (and `is_visible_to_user = True`,
because unlike the internal agents these roles are meant to be surfaced to the
older adult and their family).

## Combining roles per turn

At most **`MAX_ROLES_PER_TURN = 3`** roles combine in a single turn (2–3 in
practice), so the reminiscence stays focused and roles do not talk over each
other. The constant lives in `role_profiles.py`.

## Sensitive topics → boundary_guardian

Sensitive topics — life regrets (T08), deceased relatives and friends (T09),
physical health and care (T10), and family conflict — prioritize the
`boundary_guardian` role. Its job is to recognize privacy / grief / dependency /
risk signals and to pause, redirect, or gently decline. Its `boundary_rules`
include (verbatim intent):

- 绝不扮演逝者本人。 (Never role-play the deceased.)
- 不做医疗诊断或用药剂量建议。 (No medical diagnosis or dosage advice.)
- 命中敏感信号即暂停、转向或婉拒。
- 不制造过度依赖。
- demo 模式下不拨打真实急救。

This aligns with the safety rules in CLAUDE.md §7 and §9.

## Scope of this issue

This issue defines the **registry only**. It intentionally does **not**:

- implement automatic role selection (which role(s) fire on a given turn);
- add any UI for choosing or displaying roles;
- create seven separate LLM agents — the roles remain descriptive data adopted
  by the single `CompanionAgent`.

Those belong to later Phase 3 issues (#52–#54).
