from typing import List

from pydantic import BaseModel, Field

from src.matcher.analysis.models import ScoredCriterion
from src.scorecard.models.scorecard import CriterionType, ImportanceLevel


class Synthesis(BaseModel):
    strengths: List[str] = Field(description="List of strengths of the profile")
    weaknesses: List[str] = Field(description="List of weaknesses of the profile")


class ExtendedScoredCriterion(ScoredCriterion):
    description: str = Field(description="Description of the criterion")
    importance_level: ImportanceLevel = Field(
        description="Importance level of the criterion"
    )
    criterion_type: CriterionType = Field(description="Type of the criterion")
