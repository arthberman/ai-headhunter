from typing import Optional

from pydantic import BaseModel, Field

from matcher.sub_graph.decision.models import (
    ConclusionOverall,
    HierarchyMove,
    IntentToMove,
    OpenessToWork,
    RedflagStability,
)


class OutputDecisionSchema(BaseModel):
    """Output decision schema."""

    conclusion: Optional[ConclusionOverall] = Field(default=None)
    decision_hierarchy_move: Optional[HierarchyMove] = Field(default=None)
    decision_openess_to_work: Optional[OpenessToWork] = Field(default=None)
    decision_intent_to_move: Optional[IntentToMove] = Field(default=None)
    decision_redflag_stability: Optional[RedflagStability] = Field(default=None)
