"""Conditional routing: map a Coordinator route to its response pipeline.

The companion route reads memory before the reply and extracts memory after it;
other routes are a single node. Returning a list keeps the runner uniform.
"""

from __future__ import annotations

from typing import Callable

from app.core.constants import Route
from app.graph.nodes import (
    GraphDeps,
    companion_node,
    memory_read_node,
    memory_write_node,
    proactive_node,
    reminder_node,
    retrieval_node,
    safety_node,
)
from app.graph.state import GraphState

Node = Callable[[GraphState, GraphDeps], GraphState]

_SAFETY_ROUTES = {Route.safety_response, Route.emergency_mock}


def response_pipeline(route: Route | None) -> list[Node]:
    if route in _SAFETY_ROUTES:
        return [safety_node]
    if route == Route.reminder_management:
        return [reminder_node]
    if route == Route.proactive_checkin:
        return [proactive_node]
    if route == Route.retrieval_supported_response:
        # Retrieve the external fact first, then let the companion rewrite it
        # (with memory) into an elderly-friendly reply.
        return [retrieval_node, memory_read_node, companion_node, memory_write_node]
    # companion_chat answers via the companion path, reading and extracting
    # memory around the reply.
    return [memory_read_node, companion_node, memory_write_node]
