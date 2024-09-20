from pydantic import BaseModel, Field


class ScoredCriterion(BaseModel):
    """Respond to the user with this"""

    id: str = Field(..., description="Unique identifier for the criterion")
    score: float = Field(
        ..., ge=0, le=1, description="Score assigned to this criterion"
    )
    explanation: str = Field(..., description="Explanation for the assigned score")
    confidence_level: float = Field(
        ..., ge=0, le=1, description="Confidence level in the assigned score (0 to 1)"
    )
