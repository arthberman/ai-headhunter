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

    conclusion_overall: Optional[ConclusionOverall] = Field(default=None)
    hierarchy_move: Optional[HierarchyMove] = Field(default=None)
    openess_to_work: Optional[OpenessToWork] = Field(default=None)
    intent_to_move: Optional[IntentToMove] = Field(default=None)
    redflag_stability: Optional[RedflagStability] = Field(default=None)
