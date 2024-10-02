from typing import List, Optional

from pydantic import BaseModel, Field

from analysis_feedback.models import (
    ProfileRelatedElement,
    ScorecardRelatedElement,
    ScoredCriterion,
)
from candidate_matcher.models.profile import Profile


class MainGraphState(BaseModel):
    """State of the main graph."""

    raw_human_feedback: str = Field(default=None)
    scored_criteria: Optional[List[ScoredCriterion]] = Field(default=None)
    candidate_profile: Optional[Profile] = Field(default=None)

    human_feedback: Optional[str] = Field(default=None)
    scorecard_related_elements: Optional[ScorecardRelatedElement] = Field(default=None)
    profile_related_elements: Optional[ProfileRelatedElement] = Field(default=None)
    synthesized_feedback: Optional[str] = Field(default=None)


class InputGraphState(BaseModel):
    """State of the input graph."""

    raw_human_feedback: str = Field(default=None)
    candidate_profile: Optional[Profile] = Field(default=None)
    scored_criteria: Optional[List[ScoredCriterion]] = Field(default=None)
