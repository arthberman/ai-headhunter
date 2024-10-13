from typing import List

from pydantic import BaseModel, Field

from analysis.nodes.analysis_subgraph.models import ScoredCriterion
from scorecard.models.scorecard import CriterionType, ImportanceLevel


class Synthesis(BaseModel):
    """Synthesis of the candidate matcher."""

    strengths: List[str] = Field(description="List of strengths of the profile")
    weaknesses: List[str] = Field(description="List of weaknesses of the profile")


class ExtendedScoredCriterion(ScoredCriterion):
    """Extended scored criterion."""

    description: str = Field(description="Description of the criterion")
    importance_level: ImportanceLevel = Field(
        description="Importance level of the criterion"
    )
    criterion_type: CriterionType = Field(description="Type of the criterion")
