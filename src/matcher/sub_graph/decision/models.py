from enum import Enum

from pydantic import BaseModel, Field


class SynthesisScore(Enum):
    """Score of the synthesis."""

    PASS = "pass"
    FAIL = "fail"
    DOUBT = "doubt"


class RedflagStabilitySynthesis(BaseModel):
    """Synthesis of the candidate's redflag stability."""

    score: SynthesisScore = Field(..., description="Score of the synthesis")
    explanation: str = Field(
        ..., description="Explanation of the synthesis (max 600 characters)"
    )
