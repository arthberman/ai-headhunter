from enum import Enum

from pydantic import BaseModel, Field


class Score(Enum):
    """Score of the synthesis."""

    PASS = "pass"
    FAIL = "fail"
    DOUBT = "doubt"


class RedflagStability(BaseModel):
    """Candidate's redflag stability assessment."""

    score: Score = Field(..., description="Score of the assessment")
    explanation: str = Field(
        ..., description="Explanation of the assessment (max 600 characters)"
    )
