import operator
from typing import Annotated, List, Sequence

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from setup.state import BaseContext


class AgentState(BaseModel):
    """State of the agent."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    contexts: List[BaseContext] = Field(
        ..., description="List of all contexts related to the job posting"
    )
    loop_step: Annotated[int, operator.add] = Field(default=0)


class OutputGraphState(BaseModel):
    """State of the enrichment graph."""

    contexts: List[BaseContext] = Field(
        ..., description="List of all contexts related to the job posting"
    )
