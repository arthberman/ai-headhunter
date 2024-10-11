from enum import Enum
from typing import List, Optional
from uuid import uuid4

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
    GAUSSIAN = "GAUSSIAN"


class BaseCriterion(BaseModel):
    """Base criterion."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the criterion",
    )
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


class Scorecard(BaseModel):
    """Scorecard structure."""

    must_have_criteria: List[BaseCriterion] = Field(
        ..., description="MUST_HAVE criteria"
    )
    important_criteria: List[BaseCriterion] = Field(
        ..., description="IMPORTANT criteria"
    )
    nice_to_have_criteria: List[BaseCriterion] = Field(
        ..., description="NICE_TO_HAVE criteria"
    )
