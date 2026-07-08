"""Evaluation export models (issue #80).

Exports are derived from trace metadata so demo analysis can measure routing,
risk, retrieval, and safety coverage without exposing raw chat transcripts.
"""

from __future__ import annotations

from app.schemas.trace import TraceSummary

from pydantic import BaseModel, Field


class EvaluationExport(BaseModel):
    user_id: str
    exported_at: str
    trace_count: int = 0
    route_counts: dict[str, int] = Field(default_factory=dict)
    risk_counts: dict[str, int] = Field(default_factory=dict)
    safety_critic_turns: int = 0
    retrieval_turns: int = 0
    rows: list[TraceSummary] = Field(default_factory=list)
