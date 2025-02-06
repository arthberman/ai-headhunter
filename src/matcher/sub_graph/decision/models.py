from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Outcome(Enum):
    """Outcome of the assessment."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVIEW = "review"


class Decision(BaseModel):
    """Decision of the assessment."""

    outcome: Outcome = Field(..., description="Outcome of the assessment")
    explanation: str = Field(
        ..., description="Explanation of the assessment (max 600 characters)"
    )


class Conclusion(BaseModel):
    """Overall conclusion of the matcher."""

    outcome: Outcome = Field(..., description="Outcome of the matcher")
    explanation: str = Field(
        ...,
        description="Explanation of the outcome in one-line paragraph (max 600 characters)",
    )
    summary: List[str] = Field(
        ...,
        description="""Summary of the conclusion as a list of bullet points.
        Use an emoji at the beginning of each element. Focus on the elements
        that were structural in your decisions. Max 70 characters per item""",
    )
