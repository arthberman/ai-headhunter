from typing import List

from pydantic import BaseModel, Field


class ScoredCriterion(BaseModel):
    """Respond to the user with this."""

    id: str = Field(..., description="Unique identifier for the criterion")
    score: float = Field(
        ..., ge=0, le=1, description="Score assigned to this criterion"
    )
    explanation: str = Field(..., description="Explanation for the assigned score")
    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence level in the assigned score (0 to 1)",
    )


class Question(BaseModel):
    """A question to answer."""

    text: str = Field(..., description="The question to answer")
    purpose: str = Field(..., description="The purpose of the question")


class CotQuestions(BaseModel):
    """List of questions to answer."""

    questions: List[Question] = Field(..., description="List of questions to answer")
