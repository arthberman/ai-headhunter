from pydantic import BaseModel, Field


class CareerPathOutput(BaseModel):
    """Output for career path."""

    score_intent: float = Field(
        description="Score of the career path, must be 0.1, 0.3, 0.6 or 0.9"
    )
    explanation_intent: str = Field(description="Explanation of the career path score")

    score_hierarchy: float = Field(
        description="Score of the career path hierarchy, must be 0.1, 0.3, 0.6 or 0.9"
    )
    explanation_hierarchy: str = Field(
        description="Explanation of the career path hierarchy score"
    )
