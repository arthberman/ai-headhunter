from typing import Annotated

from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field

from matcher.models.profile import Profile


class FeedbackChatGraphState(BaseModel):
    """State of the feedback chat."""

    profile: Profile = Field(...)
    selected_elements: str = Field(...)
    job_synthesis: str = Field(...)
    rules_met: bool = Field(default=False)

    messages: Annotated[list[AnyMessage], add_messages] = Field(default_factory=list)
