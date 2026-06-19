"""CoordinatorAgent — deterministic routing policy (issue #5).

Decides one route per turn from the InputRuleGuard risk classification and
whether a StateEvent is present. It is an *agent* (it owns the routing policy and
its decisions are explainable), not a tool. It never calls an LLM and never runs
SafetyCritic itself — low-risk turns simply route to the companion path.

Slice-3 wires the companion, safety, and (dormant) proactive routes. The
reminder / memory / retrieval routes exist in the Route vocabulary and hook in
with their slices (#10 / #11 / #13); #22 populates ``state_event``.
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
        has_state_event: bool,
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

        if has_state_event:
            return RouteDecision(
                route=Route.proactive_checkin,
                reason="存在 StateEvent，路由到 Guardian 主动关怀路径",
            )

        return RouteDecision(
            route=Route.companion_chat,
            reason="低风险普通对话，进入陪伴路径（不调用 SafetyCritic）",
        )
