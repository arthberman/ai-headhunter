import operator
from typing import Annotated, List, Sequence

from langchain_core.messages import BaseMessage
from langgraph.store.base import Op
from pydantic import BaseModel, Field

from analysis.state import MainGraphState
from scorecard.models.scorecard import BaseCriterion


class AnalysisMainState(BaseModel):
    """State for the analysis graph."""

    main_state: MainGraphState
    messages: Annotated[Sequence[BaseMessage], operator.add]
    criterion: BaseCriterion = Field(...)
    loop_step: Annotated[int, operator.add] = Field(default=0)
    batch_store_ops: Annotated[List[Op], operator.add] = Field(default_factory=list)
