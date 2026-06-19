"""Conditional routing: map a Coordinator route to the response node (issue #5)."""

from __future__ import annotations

from typing import Callable

from app.core.constants import Route
from app.graph.nodes import GraphDeps, companion_node, proactive_node, safety_node
from app.graph.state import GraphState

ResponseNode = Callable[[GraphState, GraphDeps], GraphState]

_SAFETY_ROUTES = {Route.safety_response, Route.emergency_mock}


def select_response_node(route: Route | None) -> ResponseNode:
    if route in _SAFETY_ROUTES:
        return safety_node
    if route == Route.proactive_checkin:
        return proactive_node
    # companion_chat and (until their slices land) reminder / memory /
    # retrieval all answer via the companion path for now.
    return companion_node
