from typing import List, Optional

from pydantic import BaseModel, Field

from analysis.feedback.models import (
    ProfileRelatedElement,
    ScorecardRelatedElement,
    ScoredCriterion,
)
from analysis.models.profile import Profile


class InputGraphState(BaseModel):
    """State of the input graph."""

    raw_human_feedback: str = Field(...)
    candidate_profile: Profile = Field(...)
    scored_criteria: List[ScoredCriterion] = Field(...)
    scorecard_synthesis: str = Field(...)


class MainGraphState(InputGraphState):
    """State of the main graph."""

    human_feedback: Optional[str] = Field(default=None)
    scorecard_related_elements: Optional[ScorecardRelatedElement] = Field(default=None)
    profile_related_elements: Optional[ProfileRelatedElement] = Field(default=None)
    synthesized_feedback: Optional[str] = Field(default=None)
    is_actionable_and_relevant: Optional[bool] = Field(default=None)
