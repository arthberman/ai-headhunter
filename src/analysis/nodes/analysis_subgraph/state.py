import operator
from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from analysis.iterative.state import MainGraphState
from scorecard.models.scorecard import BaseCriterion


class AnalysisMainState(BaseModel):
    """State for the analysis graph."""

    main_state: MainGraphState
    messages: Annotated[Sequence[BaseMessage], operator.add]
    criterion: BaseCriterion = Field(...)
    loop_step: Annotated[int, operator.add] = Field(default=0)
