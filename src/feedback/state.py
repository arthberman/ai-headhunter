from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from matcher.models.profile import Profile
from setup.models.scorecard import Scorecard


class FeedbackClassifier(str, Enum):
    """Classifier for feedback."""

    POSITIVE = "positive"
    CONCERN = "concern"


class FeedbackInputGraphState(BaseModel):
    """State of the feedback input graph."""

    scorecard: Scorecard = Field(...)
    profile: Profile = Field(...)
    feedback: str = Field(...)
    context_provided: Optional[str] = Field(None)


class FeedbackGraphState(FeedbackInputGraphState):
    """State of the feedback graph."""

    classifier: Optional[FeedbackClassifier] = Field(
        None,
        description="The classifier for the feedback : positive or concern.",
    )

    pass


class FeedbackOutputGraphState(FeedbackInputGraphState):
    """State of the feedback output graph."""

    pass
