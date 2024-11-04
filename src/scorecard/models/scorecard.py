from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class ImportanceLevel(str, Enum):
    """Importance level of the criterion."""

    MUST_HAVE = "MUST_HAVE"
    NICE_TO_HAVE = "NICE_TO_HAVE"


class CriterionType(str, Enum):
    """Criterion type."""

    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    HARD_SKILL = "HARD_SKILL"
    SOFT_SKILL = "SOFT_SKILL"
    INDUSTRY_KNOWLEDGE = "INDUSTRY_KNOWLEDGE"
    PERSONA = "PERSONA"
    LOCATION = "LOCATION"
    LANGUAGE = "LANGUAGE"
    ADDITIONAL_QUALIFICATION = "ADDITIONAL_QUALIFICATION"


class ScoringDistribution(str, Enum):
    """Scoring distribution."""

    BINARY = "BINARY"
    CONTINUOUS = "CONTINUOUS"
    GAUSSIAN = "GAUSSIAN"


class BaseCriterion(BaseModel):
    """Base criterion."""

    id: Optional[str] = Field(
        None, description="Unique identifier for the criterion (UUID)"
    )
    description: str = Field(..., description="Detailed description of the criterion")
    type: CriterionType = Field(
        ...,
        description="Type of the criterion (EDUCATION, EXPERIENCE, LANGUAGE, HARD_SKILL, SOFT_SKILL, INDUSTRY_KNOWLEDGE, ADDITIONAL_QUALIFICATION, PERSONA, LOCATION)",
    )
    importance_level: ImportanceLevel = Field(
        ...,
        description="Importance level of the criterion (MUST_HAVE, NICE_TO_HAVE)",
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

    criteria: List[BaseCriterion] = Field(
        default_factory=list, description="List of criteria in the scorecard"
    )

    is_updating: bool = Field(
        default=False,
        description="Whether the scorecard is updating, defaults to False",
    )

    @model_validator(mode="after")
    def validate_importance_levels(self) -> "Scorecard":
        """Validate the importance levels only when not updating."""
        if not self.is_updating:
            must_have_count = sum(
                1
                for c in self.criteria
                if c.importance_level == ImportanceLevel.MUST_HAVE
            )
            nice_to_have_count = sum(
                1
                for c in self.criteria
                if c.importance_level == ImportanceLevel.NICE_TO_HAVE
            )

            if must_have_count < 2:
                raise ValueError("There must be at least 2 MUST_HAVE criteria")
            if nice_to_have_count < 2:
                raise ValueError("There must be at least 2 NICE_TO_HAVE criteria")

        return self

    @model_validator(mode="after")
    def validate_required_criterion_types(self) -> "Scorecard":
        """Validate that there is at least one criterion for Language and Location."""
        if not self.is_updating:
            criteria_types = [c.type for c in self.criteria]
            required_types = [
                CriterionType.LANGUAGE,
                CriterionType.LOCATION,
            ]

            for required_type in required_types:
                if required_type not in criteria_types:
                    raise ValueError(
                        f"There must be at least 1 criterion of type {required_type}"
                    )

        return self
