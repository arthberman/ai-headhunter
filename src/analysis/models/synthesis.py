from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class SynthesisScore(Enum):
    """Score of the synthesis."""

    PASS = "PASS"
    FAIL = "FAIL"
    DOUBT = "DOUBT"


class LocationSynthesis(BaseModel):
    """Synthesis of the analysis of the candidate's location relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class MustSynthesis(BaseModel):
    """Synthesis of the analysis of the candidate's must criteria relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class NiceSynthesis(BaseModel):
    """Synthesis of the analysis of the candidate's nice criteria relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class CultureSynthesis(BaseModel):
    """Synthesis of the analysis of the candidate's culture relative to the company culture."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class IntentSynthesis(BaseModel):
    """Synthesis of the analysis of the candidate's intent to be open to opportunities."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class HierarchySynthesis(BaseModel):
    """Synthesis of the analysis of the candidate's hierarchy relative to the job."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )


class Synthesis(BaseModel):
    """Synthesis of the candidate matcher."""

    strengths: List[str] = Field(description="List of strengths of the profile")
    weaknesses: List[str] = Field(description="List of weaknesses of the profile")
