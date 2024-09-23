from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ImportanceLevel(str, Enum):
    """Importance level of the criterion."""

    MUST_HAVE = "MUST_HAVE"
    IMPORTANT = "IMPORTANT"
    NICE_TO_HAVE = "NICE_TO_HAVE"


class CriterionType(str, Enum):
    """Criterion type."""

    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    LANGUAGE = "LANGUAGE"
    HARD_SKILL = "HARD_SKILL"
    SOFT_SKILL = "SOFT_SKILL"
    INDUSTRY_KNOWLEDGE = "INDUSTRY_KNOWLEDGE"
    ADDITIONAL_QUALIFICATION = "ADDITIONAL_QUALIFICATION"


class ScoringDistribution(str, Enum):
    """Scoring distribution."""

    BINARY = "BINARY"
    CONTINUOUS = "CONTINUOUS"
    ORDINAL = "ORDINAL"
    GAUSSIAN = "GAUSSIAN"


class BaseCriterion(BaseModel):
    """Base criterion."""

    id: Optional[str] = Field(None, description="Unique identifier for the criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    type: CriterionType = Field(
        ...,
        description="Type of the criterion (EDUCATION, EXPERIENCE, LANGUAGE, HARD_SKILL, SOFT_SKILL, INDUSTRY_KNOWLEDGE, ADDITIONAL_QUALIFICATION)",
    )
    context: Optional[str] = Field(
        None,
        description="This is the context of the job posting that is relevant to the criterion (definition of the scope).",
    )
    scoring_distribution: Optional[ScoringDistribution] = Field(
        None,
        description="The type of scoring distribution for this criterion",
    )
    distribution_params: Optional[Dict[str, float]] = Field(
        None,
        description="Parameters specific to the chosen scoring distribution",
    )


class Scorecard(BaseModel):
    """Scorecard structure."""

    mustHaveCriteria: List[BaseCriterion] = Field(..., description="MUST_HAVE criteria")
    importantCriteria: List[BaseCriterion] = Field(
        ..., description="IMPORTANT criteria"
    )
    niceToHaveCriteria: List[BaseCriterion] = Field(
        ..., description="NICE_TO_HAVE criteria"
    )
