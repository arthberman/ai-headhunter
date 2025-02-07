from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from matcher.sub_graph.decision.models import Conclusion, Decision, reducer_decisions


class OutputDecisionSchema(BaseModel):
    """Output decision schema."""

    conclusion: Optional[Conclusion] = Field(default=None)
    decisions: Annotated[List[Decision], reducer_decisions] = Field(
        default_factory=list
    )
