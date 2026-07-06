"""CoordinatorAgent — deterministic routing policy (issue #5).

Decides one route per turn from the InputRuleGuard risk classification and
whether a StateEvent is present. It is an *agent* (it owns the routing policy and
its decisions are explainable), not a tool. It never calls an LLM and never runs
SafetyCritic itself — low-risk turns simply route to the companion path.

Wires the companion, safety, (dormant) proactive, and reminder routes. Memory is
read/written on the companion path (#10); the retrieval route hooks in with #13;
#22 populates ``state_event``.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.core.constants import RiskLevel, Route
from app.safety.risk_classifier import RiskClassification

_EMERGENCY_CATEGORIES = {"fall_no_response", "emergency_help"}


@dataclass
class RouteDecision:
    route: Route
    reason: str


class CoordinatorAgent:
    name = "CoordinatorAgent"

    def decide(
        self,
        *,
        classification: RiskClassification,
        has_state_event: bool = False,
        reminder_intent: bool = False,
        retrieval_intent: bool = False,
        reminiscence_cue_intent: bool = False,
    ) -> RouteDecision:
        if (
            classification.level == RiskLevel.crisis
            and classification.category in _EMERGENCY_CATEGORIES
        ):
            return RouteDecision(
                route=Route.emergency_mock,
                reason=f"检测到紧急情况（{classification.category}），进入 mock 紧急关怀路径",
            )

        if classification.is_risky:
            return RouteDecision(
                route=Route.safety_response,
                reason=(
                    f"检测到高风险（{classification.category}/"
                    f"{classification.level.value}），进入安全路径"
                ),
            )

        # Reminder requests are low-risk; medication dosage questions are caught
        # by the risk checks above, so they never reach here.
        if reminder_intent:
            return RouteDecision(
                route=Route.reminder_management,
                reason="检测到提醒请求，路由到 ReminderTool 管理路径",
            )

        # Only time-sensitive external facts (weather / air quality) retrieve.
        # Emotional / reminiscence turns never reach here (no retrieval intent),
        # and dosage questions were already routed to safety above.
        if retrieval_intent:
            return RouteDecision(
                route=Route.retrieval_supported_response,
                reason="检测到时效性外部信息需求，调用 InfoRetrievalTool",
            )

        if has_state_event:
            return RouteDecision(
                route=Route.proactive_checkin,
                reason="存在 StateEvent，路由到 Guardian 主动关怀路径",
            )

        # Non-sensitive reminiscence (old objects / old photos / work / culture /
        # family) stages 2–3 visible relationship roles into a short social cue.
        # Placed after all higher-priority checks so safety / reminder / retrieval
        # / proactive still win, and only NON-SENSITIVE topics reach here (the
        # cue-intent classifier excludes grief/health/privacy/loneliness).
        if reminiscence_cue_intent:
            return RouteDecision(
                route=Route.relationship_cueing,
                reason="检测到回忆/旧物/旧照片/工作回忆类输入，进入关系角色社会线索路径",
            )

        return RouteDecision(
            route=Route.companion_chat,
            reason="低风险普通对话，进入陪伴路径（不调用 SafetyCritic）",
        )
