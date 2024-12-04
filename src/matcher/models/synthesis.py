from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class SynthesisScore(Enum):
    """Score of the synthesis."""

    PASS = "pass"
    FAIL = "fail"
    DOUBT = "doubt"


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


class IntentSynthesis(BaseModel):
    """Synthesis of the candidate's intent to be open to opportunities."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class HierarchySynthesis(BaseModel):
    """Synthesis of the candidate's hierarchy relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class OpenToWorkSynthesis(BaseModel):
    """Synthesis of the candidate's openess to work, awareness of new opportunities."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class SynthesisOverall(BaseModel):
    """Overall synthesis of the candidate matcher."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ...,
        description="Explanation of the score in one-line paragraph (max 600 characters)",
    )
    summary: List[str] = Field(
        ...,
        description="""Summary of the synthesis as a list of bullet points.
        Use an emoji at the beginning of each element. Focus on the elements
        that were structural in your decisions. Max 70 characters per item""",
    )
