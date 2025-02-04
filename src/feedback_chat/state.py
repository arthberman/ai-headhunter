from typing import Annotated, List

from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field


class FeedbackChatInputGraphState(BaseModel):
    """State of the feedback chat input."""

    profile: str = Field(...)
    selected_elements: List[str] = Field(...)
    job_synthesis: str = Field(...)
    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)


class FeedbackChatGraphState(FeedbackChatInputGraphState):
    """State of the feedback chat."""

    rules_met: bool = Field(default=False)
