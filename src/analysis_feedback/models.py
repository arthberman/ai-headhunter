from typing import List, Optional

from pydantic import BaseModel, Field

from scorecard_generator.models.scorecard import BaseCriterion


class ScoredCriterion(BaseCriterion):
    """Scored criterion."""

    score: float = Field(default=None)
    confidence_level: float = Field(default=None)


class ProfileRelatedElement(BaseModel):
    """Element(s) from the profile related to the human feedback provided."""

    description: Optional[str] = Field(
        default=None,
        description="Description of element(s) from the profile related to the human feedback provided.",
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of why the element(s) are related to the human feedback provided.",
    )


class ScorecardRelatedElement(BaseModel):
    """Element(s) from the scorecard related to the human feedback provided."""

    criteria: Optional[List[ScoredCriterion]] = Field(
        default=None,
        description="Criteria from the scorecard related to the human feedback provided.",
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Explanation of why the criteria are related to the human feedback provided.",
    )


class ReformedHumanFeedback(BaseModel):
    """Reformed Human feedback."""

    human_feedback: str = Field(default=None)


class SynthesizedFeedback(BaseModel):
    """Synthesized feedback."""

    synthesized_feedback: str = Field(default=None)
    is_actionable_and_relevant: bool = Field(default=None)
