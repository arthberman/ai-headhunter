from typing import Optional

from pydantic import BaseModel, Field

from matcher.models.profile import Profile
from setup.models.scorecard import Scorecard


class FeedbackInputGraphState(BaseModel):
    """State of the feedback input graph."""

    scorecard: Scorecard = Field(...)
    profile: Profile = Field(...)
    feedback: str = Field(...)
    provided_context: Optional[str] = Field(None)


class FeedbackGraphState(FeedbackInputGraphState):
    """State of the feedback graph."""

    pass


class FeedbackOutputGraphState(FeedbackInputGraphState):
    """State of the feedback output graph."""

    pass
