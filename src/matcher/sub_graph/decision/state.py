from typing import Optional

from pydantic import BaseModel, Field

from matcher.sub_graph.decision.models import Conclusion, Decision


class OutputDecisionSchema(BaseModel):
    """Output decision schema."""

    conclusion: Optional[Conclusion] = Field(default=None)
    decision_hierarchy_move: Optional[Decision] = Field(default=None)
    decision_openess_to_work: Optional[Decision] = Field(default=None)
    decision_intent_to_move: Optional[Decision] = Field(default=None)
    decision_redflag_stability: Optional[Decision] = Field(default=None)
