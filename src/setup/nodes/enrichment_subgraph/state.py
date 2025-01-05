import operator
from typing import Annotated, List, Sequence

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from setup.state import BaseResource


class AgentState(BaseModel):
    """State of the agent."""

    messages: Annotated[Sequence[BaseMessage], operator.add]
    resources: List[BaseResource] = Field(
        ..., description="List of all resources related to the job posting"
    )
    loop_step: Annotated[int, operator.add] = Field(default=0)


class OutputGraphState(BaseModel):
    """State of the enrichment graph."""

    resources: List[BaseResource] = Field(
        ..., description="List of all resources related to the job posting"
    )
