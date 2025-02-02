from enum import Enum

from pydantic import BaseModel, Field


class SynthesisScore(Enum):
    """Score of the synthesis."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVIEW = "review"


class LocationSynthesis(BaseModel):
    """Synthesis of the candidate's location relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class MustSynthesis(BaseModel):
    """Synthesis of the candidate's must criteria relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )
