import operator
from typing import Annotated, List, Sequence

from langchain_core.messages import BaseMessage
from langgraph.store.base import Op
from pydantic import BaseModel, Field

from analysis.state import MainGraphState
from scorecard.models.scorecard import BaseCriterion


class InputAnalysisMainState(BaseModel):
    """Input state for the analysis graph."""

    main_state: MainGraphState
    criterion: BaseCriterion = Field(...)


class AnalysisMainState(InputAnalysisMainState):
    """State for the analysis graph."""

    messages: Annotated[Sequence[BaseMessage], operator.add] = Field(
        default_factory=list
    )
    loop_step: Annotated[int, operator.add] = Field(default=0)
    batch_store_ops: Annotated[List[Op], operator.add] = Field(default_factory=list)
