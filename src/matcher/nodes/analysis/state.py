import operator
from typing import Annotated, Sequence, List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from matcher.nodes.analysis.models import ScoredCriterion
from matcher.state import MainGraphState


class AnalysisOutputState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# Define the AgentState
class AnalysisMainState(BaseModel):
    main_state: MainGraphState
    messages: Annotated[Sequence[BaseMessage], operator.add]
    criterion_id: str = Field(..., description="Criterion ID")
    criterion_description: str = Field(..., description="Criterion description")
    criterion_context: str = Field(..., description="Criterion context")
