import operator
from typing import Annotated, Sequence, List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from matcher.state import MainGraphState
from scorecard.models.scorecard import BaseCriterion


class AnalysisOutputState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], operator.add]


# Define the AgentState
class AnalysisMainState(BaseModel):
    main_state: MainGraphState
    messages: Annotated[Sequence[BaseMessage], operator.add]
    criterion: BaseCriterion = Field(...)
    loop_step: Annotated[int, operator.add] = Field(default=0)
