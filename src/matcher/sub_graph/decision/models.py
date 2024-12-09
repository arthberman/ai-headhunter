from enum import Enum
from typing import List

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


class IntentToMove(BaseModel):
    """Candidate's intent to move to new job opportunities assessment."""

    score: Score = Field(..., description="Score of the assessment")
    explanation: str = Field(
        ..., description="Explanation of the assessment (max 600 characters)"
    )


class HierarchyMove(BaseModel):
    """Assessment of whether the candidate's current hierarchical level is compatible with the target position.

    Evaluates if the candidate's current role and seniority level would be a suitable match
    for the hierarchical requirements of the new job opportunity.
    """

    score: Score = Field(..., description="Score of the assessment")
    explanation: str = Field(
        ..., description="Explanation of the assessment (max 600 characters)"
    )


class OpenessToWork(BaseModel):
    """Assessment of the candidate's openess to work, awareness of new opportunities."""

    score: Score = Field(..., description="Score of the assessment")
    explanation: str = Field(
        ..., description="Explanation of the assessment (max 600 characters)"
    )


class ConclusionOverall(BaseModel):
    """Overall conclusion of the matcher."""

    score: Score = Field(..., description="Score of the conclusion")
    explanation: str = Field(
        ...,
        description="Explanation of the score in one-line paragraph (max 600 characters)",
    )
    summary: List[str] = Field(
        ...,
        description="""Summary of the conclusion as a list of bullet points.
        Focus on the elements
        that were structural in your decisions. Max 70 characters per item""",
    )
