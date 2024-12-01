from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Priority(str, Enum):
    """Priority of the criterion."""

    REQUIRED = "required"
    PREFERRED = "preferred"


class Category(str, Enum):
    """Category."""

    LOCATION = "location"
    EDUCATION = "education"
    EXPERIENCE = "experience"
    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    LANGUAGE = "language"
    INDUSTRY_SECTOR = "industry_sector"
    COMPANY_CULTURE = "company_culture"


class ScoringDistribution(str, Enum):
    """Scoring distribution."""

    BINARY = "binary"
    CONTINUOUS = "continuous"
    GAUSSIAN = "gaussian"


class BaseCriterion(BaseModel):
    """Base criterion."""

    id: Optional[str] = Field(
        None, description="Unique identifier for the criterion (UUID)"
    )
    description: str = Field(..., description="Detailed description of the criterion")
    category: Category = Field(
        ...,
        description="Category of the criterion (education, experience, language, hard_skill, soft_skill, industry_sector, company_culture, location)",
    )
    priority: Priority = Field(
        ...,
        description="Priority of the criterion (must_have, nice_to_have)",
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
    def validate_priority_levels(self) -> "Scorecard":
        """Validate the priority levels only when not updating."""
        if not self.is_updating:
            must_have_count = sum(
                1 for c in self.criteria if c.priority == Priority.REQUIRED
            )
            nice_to_have_count = sum(
                1 for c in self.criteria if c.priority == Priority.PREFERRED
            )

            if must_have_count < 2:
                raise ValueError("There must be at least 2 must_have criteria")
            if nice_to_have_count < 2:
                raise ValueError("There must be at least 2 nice_to_have criteria")

        return self

    @model_validator(mode="after")
    def validate_required_criterion_types(self) -> "Scorecard":
        """Validate that there is exactly one must_have location criterion and at least one language criterion."""
        if not self.is_updating:
            # Check for exactly one must_have location criterion
            location_must_have_criteria = [
                c
                for c in self.criteria
                if c.category == Category.LOCATION and c.priority == Priority.REQUIRED
            ]
            if len(location_must_have_criteria) != 1:
                raise ValueError(
                    "There must be exactly 1 must_have criterion of type location"
                )

            # Check for at least one language must_have criterion
            if not any(
                c.category == Category.LANGUAGE and c.priority == Priority.REQUIRED
                for c in self.criteria
            ):
                raise ValueError(
                    "There must be at least 1 must_have criterion of type language"
                )

        return self

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "Scorecard":
        """Validate that all criteria have unique IDs if they are present."""
        if not self.is_updating:
            # Collect all non-None IDs
            ids = [
                criterion.id for criterion in self.criteria if criterion.id is not None
            ]

            # Check for duplicates using set comparison
            if len(ids) != len(set(ids)):
                raise ValueError("All criteria must have unique IDs")

        return self
