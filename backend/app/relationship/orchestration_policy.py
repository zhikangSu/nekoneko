"""Deterministic role-scheduling policy for reminiscence turns (issue #52).

Given a classified :class:`Topic` and the registry of visible relationship
roles, :func:`decide` picks which roles speak, which one leads, how they are
cued into the turn, and emits an explainable role/topic/memory/boundary trace.

This is pure rules/templates — NO LLM. It schedules VISIBLE relationship
personas (from #51); those personas are not autonomous agents. This module does
not touch any existing graph/safety/Guardian/Reminder/Retrieval path.

Policy summary (per topic):

* old_object_photo / work_collective / general_reminiscence
  → [same_age_peer, curious_junior, middle_age_bridge], primary same_age_peer,
    cueing agent_agent_then_invite.
* family_education
  → [same_age_peer, middle_age_bridge, curious_junior], primary middle_age_bridge,
    cueing agent_agent_then_invite.
* culture_arts
  → [theme_companion, same_age_peer, curious_junior], primary theme_companion,
    cueing agent_agent_then_invite.
* SENSITIVE (deceased_grief / privacy_family_conflict / health_care) or
  risk_flags signalling these
  → [boundary_guardian, elder_mentor], primary boundary_guardian, cueing
    no_cue, explicit boundary notes, no memory card.
* loneliness_mood
  → [elder_mentor, same_age_peer], primary elder_mentor, cueing
    single_role_prelude.

Overrides applied on top of the base plan:

* Long/specific non-sensitive narrative → single role picks up the thread
  (primary only, cueing direct).
* user_role_preferences: dislike-of-follow-up drops curious_junior; wants to
  self-narrate / prefers no AI → [no_ai_role], cueing no_cue.
* selected roles are capped at MAX_ROLES_PER_TURN, always valid registry roles,
  and no_ai_role never sits beside a speaking role.
"""

from __future__ import annotations

from app.relationship.role_profiles import MAX_ROLES_PER_TURN
from app.schemas.relationship import (
    CueingStyle,
    OrchestrationInput,
    RelationshipDecision,
    RoleId,
    RoleSelectionMode,
    RoleProfile,
)
from app.relationship.topic_classifier import SENSITIVE_TOPICS, Topic

# Heuristic: an utterance this long (chars) already carries a specific, developed
# narrative, so a single role should just pick up the thread rather than staging
# a multi-persona prelude.
_LONG_NARRATIVE_CHARS = 60

# Base role plans per topic: (selected_roles, primary_role, cueing_style).
_PEER_SET = [RoleId.same_age_peer, RoleId.curious_junior, RoleId.middle_age_bridge]

_BASE_PLANS: dict[Topic, tuple[list[RoleId], RoleId, CueingStyle]] = {
    Topic.old_object_photo: (
        list(_PEER_SET),
        RoleId.same_age_peer,
        CueingStyle.agent_agent_then_invite,
    ),
    Topic.work_collective: (
        list(_PEER_SET),
        RoleId.same_age_peer,
        CueingStyle.agent_agent_then_invite,
    ),
    Topic.general_reminiscence: (
        list(_PEER_SET),
        RoleId.same_age_peer,
        CueingStyle.agent_agent_then_invite,
    ),
    Topic.family_education: (
        [RoleId.same_age_peer, RoleId.middle_age_bridge, RoleId.curious_junior],
        RoleId.middle_age_bridge,
        CueingStyle.agent_agent_then_invite,
    ),
    Topic.culture_arts: (
        [RoleId.theme_companion, RoleId.same_age_peer, RoleId.curious_junior],
        RoleId.theme_companion,
        CueingStyle.agent_agent_then_invite,
    ),
    Topic.loneliness_mood: (
        [RoleId.elder_mentor, RoleId.same_age_peer],
        RoleId.elder_mentor,
        CueingStyle.single_role_prelude,
    ),
    Topic.other: (
        [RoleId.same_age_peer, RoleId.curious_junior],
        RoleId.same_age_peer,
        CueingStyle.single_role_prelude,
    ),
}

_TOPIC_LABEL_ZH: dict[Topic, str] = {
    Topic.old_object_photo: "旧物/老照片",
    Topic.work_collective: "工作/集体生活",
    Topic.family_education: "家庭/孩子教育",
    Topic.culture_arts: "戏曲/地方文化",
    Topic.deceased_grief: "已故亲友/悲伤",
    Topic.health_care: "身体健康照护",
    Topic.privacy_family_conflict: "隐私/家庭矛盾",
    Topic.loneliness_mood: "孤单情绪",
    Topic.general_reminiscence: "一般回忆",
    Topic.other: "其他/未识别",
}

_ROLE_LABEL_ZH: dict[RoleId, str] = {
    RoleId.same_age_peer: "同龄共鸣者",
    RoleId.curious_junior: "晚辈好奇者",
    RoleId.middle_age_bridge: "中年传承者",
    RoleId.elder_mentor: "长辈引导者",
    RoleId.theme_companion: "主题陪伴者",
    RoleId.memory_organizer: "回忆整理者",
    RoleId.boundary_guardian: "边界守护者",
    RoleId.no_ai_role: "不需要AI角色",
}


def _risk_flags_signal_sensitive(risk_flags: dict | None) -> bool:
    """True if risk_flags indicate a grief/health/privacy-conflict concern."""

    if not risk_flags:
        return False
    sensitive_keys = {
        "deceased",
        "deceased_grief",
        "grief",
        "health",
        "health_care",
        "medical",
        "privacy",
        "privacy_family_conflict",
        "family_conflict",
        "conflict",
        "self_harm",
        "suicidal",
    }
    for key, value in risk_flags.items():
        if not value:
            continue
        key_norm = str(key).lower()
        if any(sk in key_norm for sk in sensitive_keys):
            return True
    return False


def _pref_dislikes_follow_up(prefs: dict | None) -> bool:
    if not prefs:
        return False
    blob = " ".join(str(v) for v in prefs.values()) + " " + " ".join(str(k) for k in prefs)
    negative = any(prefs.get(k) for k in ("dislike_follow_up", "no_follow_up", "不喜欢连续追问"))
    textual = "不喜欢连续追问" in blob or "不要追问" in blob or "少追问" in blob
    return negative or textual


def _pref_wants_solo_or_no_ai(prefs: dict | None) -> bool:
    if not prefs:
        return False
    blob = " ".join(str(v) for v in prefs.values()) + " " + " ".join(str(k) for k in prefs)
    flagged = any(
        prefs.get(k)
        for k in ("only_self_narrate", "self_narrate", "no_ai", "prefers_no_ai", "只想自己讲")
    )
    textual = (
        "只想自己讲" in blob
        or "自己讲" in blob
        or "不需要ai" in blob.lower()
        or "不需要 ai" in blob.lower()
        or "不用ai" in blob.lower()
    )
    return flagged or textual


def _manual_requested_roles(inp: OrchestrationInput, registry_ids: set[RoleId]) -> list[RoleId]:
    """Sanitize roles explicitly selected by the user for manual mode."""

    if inp.role_selection_mode is not RoleSelectionMode.manual:
        return []
    requested = [r for r in inp.selected_role_ids if r in registry_ids]
    if RoleId.no_ai_role in requested:
        return [RoleId.no_ai_role]
    return _cap_and_sanitize(
        [r for r in requested if r is not RoleId.no_ai_role],
        registry_ids,
    )


def _cap_and_sanitize(roles: list[RoleId], registry_ids: set[RoleId]) -> list[RoleId]:
    """Keep only known roles, dedupe preserving order, cap at MAX_ROLES_PER_TURN."""

    seen: set[RoleId] = set()
    cleaned: list[RoleId] = []
    for r in roles:
        if r in registry_ids and r not in seen:
            cleaned.append(r)
            seen.add(r)
    return cleaned[:MAX_ROLES_PER_TURN]


def _memory_trace(memory_context: list[str]) -> str:
    if not memory_context:
        return "未使用记忆"
    shown = "；".join(memory_context[:3])
    return f"参考了记忆片段：{shown}"


def decide(
    inp: OrchestrationInput,
    topic: Topic,
    roles: list[RoleProfile],
) -> RelationshipDecision:
    """Decide which visible roles speak for this reminiscence turn.

    Deterministic rules only. ``roles`` is the visible-role registry; no role
    outside it is ever selected.
    """

    registry_ids = {p.role_id for p in roles}
    topic_label = _TOPIC_LABEL_ZH.get(topic, topic.value)
    prefs = inp.user_role_preferences
    memory_context = inp.memory_context or []

    is_sensitive = topic in SENSITIVE_TOPICS or _risk_flags_signal_sensitive(inp.risk_flags)

    boundary_notes: list[str] = []
    should_generate_memory_card = False

    # ----- SENSITIVE path: restraint first, boundary_guardian leads ----------
    if is_sensitive:
        selected = _cap_and_sanitize(
            [RoleId.boundary_guardian, RoleId.elder_mentor], registry_ids
        )
        primary = RoleId.boundary_guardian if RoleId.boundary_guardian in selected else (
            selected[0] if selected else None
        )
        cueing = CueingStyle.no_cue

        boundary_notes.append("敏感话题：不进行角色之间的互动铺垫，由边界守护者温和地接住。")
        if topic is Topic.deceased_grief or _risk_flags_signal_sensitive(inp.risk_flags):
            # explicit deceased note whenever grief is on the table
            if topic is Topic.deceased_grief:
                boundary_notes.append("绝不扮演逝者本人，只做温和的陪伴与哀伤承接。")
        if topic is Topic.health_care:
            boundary_notes.append("不做医疗诊断/剂量建议，必要时建议联系医生、家人或急救。")
        if topic is Topic.privacy_family_conflict:
            boundary_notes.append("尊重隐私，不追问细节，不评判家庭矛盾。")

        reason = (
            f"话题判定为敏感（{topic_label}），优先由边界守护者克制地承接，"
            "不使用角色互动铺垫，也不自动生成回忆卡片。"
        )
        role_names = "、".join(_ROLE_LABEL_ZH.get(r, r.value) for r in selected)
        role_trace = f"选择 {role_names}：敏感话题以边界守护者为主，长辈引导者提供温和陪伴。"
        topic_trace = f"话题分类：{topic_label}（敏感）。"
        boundary_trace = "已触发边界克制：暂停/转向，明确不扮演逝者、不做医疗建议、不追问隐私。"
        summary = f"{topic_label} → 敏感路径：{role_names}（{cueing.value}）"

        return RelationshipDecision(
            topic=topic.value,
            selected_roles=selected,
            primary_role=primary,
            cueing_style=cueing,
            role_selection_reason=reason,
            boundary_notes=boundary_notes,
            should_generate_memory_card=False,
            trace_visible_summary=summary,
            role_trace=role_trace,
            topic_trace=topic_trace,
            memory_trace=_memory_trace(memory_context),
            boundary_trace=boundary_trace,
        )

    # ----- Manual role choice: current user control beats topic defaults -----
    manual_roles = _manual_requested_roles(inp, registry_ids)
    if manual_roles:
        if manual_roles == [RoleId.no_ai_role]:
            reason = "用户手动选择不需要 AI 角色，仅留出空间，不安排任何发言角色。"
            boundary_notes.append("尊重用户不需要 AI 的选择，不强行加入对话。")
            role_trace = "用户手动选择 不需要AI角色：完全把空间留给老人或真人陪伴。"
            topic_trace = f"话题分类：{topic_label}；但用户手动选择优先于话题默认角色。"
            boundary_trace = "已遵从用户手动选择：不安排 AI 角色发言。"
            summary = f"{topic_label} → 用户自选无 AI（{CueingStyle.no_cue.value}）"
            return RelationshipDecision(
                topic=topic.value,
                selected_roles=manual_roles,
                primary_role=RoleId.no_ai_role,
                cueing_style=CueingStyle.no_cue,
                role_selection_reason=reason,
                boundary_notes=boundary_notes,
                should_generate_memory_card=False,
                trace_visible_summary=summary,
                role_trace=role_trace,
                topic_trace=topic_trace,
                memory_trace=_memory_trace(memory_context),
                boundary_trace=boundary_trace,
            )

        primary = manual_roles[0]
        cueing = (
            CueingStyle.single_role_prelude
            if len(manual_roles) == 1
            else CueingStyle.agent_agent_then_invite
        )
        role_names = "、".join(_ROLE_LABEL_ZH.get(r, r.value) for r in manual_roles)
        primary_name = _ROLE_LABEL_ZH.get(primary, primary.value)
        should_generate_memory_card = topic in {
            Topic.old_object_photo,
            Topic.work_collective,
            Topic.family_education,
            Topic.culture_arts,
            Topic.general_reminiscence,
        }
        reason = (
            f"用户手动选择 {role_names}，本轮按自选角色组织发言，"
            f"以{primary_name}为主；话题分类仍记录为{topic_label}。"
        )
        boundary_notes.append("用户自选角色已生效；仍不扮演任何真实熟人或家人。")
        role_trace = f"用户自选 {role_names}（主：{primary_name}），系统未改用话题默认角色组。"
        topic_trace = f"话题分类：{topic_label}（非敏感）；角色来源：用户自选。"
        boundary_trace = "非敏感话题，允许用户自选关系角色；仍保留不扮演真实熟人的边界。"
        summary = f"{topic_label} → 用户自选 {role_names}（{cueing.value}）"
        return RelationshipDecision(
            topic=topic.value,
            selected_roles=manual_roles,
            primary_role=primary,
            cueing_style=cueing,
            role_selection_reason=reason,
            boundary_notes=boundary_notes,
            should_generate_memory_card=should_generate_memory_card,
            trace_visible_summary=summary,
            role_trace=role_trace,
            topic_trace=topic_trace,
            memory_trace=_memory_trace(memory_context),
            boundary_trace=boundary_trace,
        )

    # ----- Preference: elder prefers no AI / just wants to self-narrate -------
    if _pref_wants_solo_or_no_ai(prefs):
        selected = _cap_and_sanitize([RoleId.no_ai_role], registry_ids)
        primary = selected[0] if selected else None
        reason = "用户偏好自己讲述或不需要 AI 角色，仅留出空间，不安排任何发言角色。"
        boundary_notes.append("尊重用户不需要 AI 的选择，不强行加入对话。")
        role_trace = "选择 不需要AI角色：完全把空间留给老人或真人陪伴。"
        topic_trace = f"话题分类：{topic_label}；但用户偏好优先于话题。"
        boundary_trace = "已遵从用户偏好：不安排 AI 角色发言。"
        summary = f"{topic_label} → 用户偏好无 AI（{CueingStyle.no_cue.value}）"
        return RelationshipDecision(
            topic=topic.value,
            selected_roles=selected,
            primary_role=primary,
            cueing_style=CueingStyle.no_cue,
            role_selection_reason=reason,
            boundary_notes=boundary_notes,
            should_generate_memory_card=False,
            trace_visible_summary=summary,
            role_trace=role_trace,
            topic_trace=topic_trace,
            memory_trace=_memory_trace(memory_context),
            boundary_trace=boundary_trace,
        )

    # ----- Non-sensitive base plan -------------------------------------------
    base_roles, primary, cueing = _BASE_PLANS.get(
        topic, _BASE_PLANS[Topic.other]
    )
    base_roles = list(base_roles)

    # Preference: dislikes continuous follow-up → drop the curious junior.
    dropped_junior = False
    if _pref_dislikes_follow_up(prefs) and RoleId.curious_junior in base_roles:
        base_roles = [r for r in base_roles if r is not RoleId.curious_junior]
        dropped_junior = True
        if primary is RoleId.curious_junior:
            primary = base_roles[0] if base_roles else None

    # Long, specific narrative → a single role picks up the thread directly.
    long_narrative = len(inp.user_input or "") >= _LONG_NARRATIVE_CHARS
    if long_narrative:
        primary = primary if primary in base_roles else (base_roles[0] if base_roles else primary)
        base_roles = [primary] if primary is not None else base_roles
        cueing = CueingStyle.direct

    selected = _cap_and_sanitize(base_roles, registry_ids)
    if primary not in selected:
        primary = selected[0] if selected else None

    # Memory card only for clear, non-sensitive personal facts/interests.
    should_generate_memory_card = topic in {
        Topic.old_object_photo,
        Topic.work_collective,
        Topic.family_education,
        Topic.culture_arts,
        Topic.general_reminiscence,
    }

    # ----- Traces ------------------------------------------------------------
    role_names = "、".join(_ROLE_LABEL_ZH.get(r, r.value) for r in selected)
    primary_name = _ROLE_LABEL_ZH.get(primary, primary.value) if primary else "无"

    reason_bits = [f"话题为{topic_label}，按策略安排 {role_names}，以{primary_name}为主。"]
    if dropped_junior:
        reason_bits.append("已根据用户偏好去掉“晚辈好奇者”的连续追问。")
    if long_narrative:
        reason_bits.append("老人已给出较完整的叙述，改为单一角色直接接话，不做多角色铺垫。")
    else:
        reason_bits.append(f"采用 {cueing.value} 的方式引出话题。")
    reason = "".join(reason_bits)

    role_trace = f"选择 {role_names}（主：{primary_name}）：{topic_label}适合这组关系功能。"
    topic_trace = f"话题分类：{topic_label}（非敏感）。"
    boundary_trace = "非敏感话题，允许正常陪伴与温和引导；仍不扮演真实熟人。"
    summary = f"{topic_label} → {role_names}（{cueing.value}）"

    boundary_notes.append("不扮演任何真实熟人或家人，只做关系功能陪伴。")

    return RelationshipDecision(
        topic=topic.value,
        selected_roles=selected,
        primary_role=primary,
        cueing_style=cueing,
        role_selection_reason=reason,
        boundary_notes=boundary_notes,
        should_generate_memory_card=should_generate_memory_card,
        trace_visible_summary=summary,
        role_trace=role_trace,
        topic_trace=topic_trace,
        memory_trace=_memory_trace(memory_context),
        boundary_trace=boundary_trace,
    )
