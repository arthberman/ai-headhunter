from enum import Enum

from pydantic import BaseModel, Field


# enum of score : go, no go or doubt
class LocationScore(Enum):
    """Score of the location analysis."""

    GO = "GO"
    NO_GO = "NO_GO"
    DOUBT = "DOUBT"


class LocationAnalysis(BaseModel):
    """Analysis of the candidate's location."""

    explanation: str = Field(
        ..., description="Explanation of the analysis (max 300 characters)"
    )
    score: LocationScore = Field(..., description="Score of the analysis")
