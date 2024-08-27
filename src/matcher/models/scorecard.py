from enum import Enum
from typing import Any, Dict, List, Optional, Union

from langchain_core.pydantic_v1 import BaseModel, Field, validator


class ImportanceLevel(str, Enum):
    MUST_HAVE = "MUST_HAVE"
    IMPORTANT = "IMPORTANT"
    NICE_TO_HAVE = "NICE_TO_HAVE"


class CriteriaType(str, Enum):
    EDUCATION = "EDUCATION"
    EXPERIENCE = "EXPERIENCE"
    LANGUAGE = "LANGUAGE"
    HARD_SKILL = "HARD_SKILL"
    SOFT_SKILL = "SOFT_SKILL"
    INDUSTRY_KNOWLEDGE = "INDUSTRY_KNOWLEDGE"
    ADDITIONAL_QUALIFICATION = "ADDITIONAL_QUALIFICATION"


class BaseCriterion(BaseModel):
    id: Optional[str] = Field(description="Unique identifier for the criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    type: CriteriaType = Field(
        ...,
        description="Type of the criterion (EDUCATION, EXPERIENCE, LANGUAGE, HARD_SKILL, SOFT_SKILL, INDUSTRY_KNOWLEDGE, ADDITIONAL_QUALIFICATION)",
    )


class MustHaveCriterion(BaseCriterion):
    weight: float = Field(
        ...,
        description="Weight of the criterion. Must be greater than 0 and less than or equal to 1.",
    )
    compensationDescription: str = Field(
        ..., description="Description of how compensation is applied"
    )
    compensationScore: float = Field(
        ...,
        description="Score applied for compensation. Must be greater than or equal to 0 and less than or equal to 1.",
    )


class ImportantCriterion(BaseCriterion):
    weight: float = Field(
        ...,
        description="Weight of the criterion. Must be greater than 0 and less than or equal to 1.",
    )


class NiceToHaveCriterion(BaseCriterion):
    maxBonusPoint: float = Field(
        ...,
        description="Maximum bonus points for this criterion. Must be greater than or equal to 0.",
    )


class MustHaveCriteria(BaseModel):
    criteria: List[MustHaveCriterion] = Field(
        ..., description="List of MUST_HAVE criteria"
    )

    @validator("criteria")
    def validate_criteria(cls, v):
        totalWeight = sum(criterion.weight for criterion in v)
        if not 0.99 <= totalWeight <= 1.01:
            raise ValueError(
                f"Sum of MUST_HAVE criteria weights must be 1, got {totalWeight}"
            )
        return v


class ImportantCriteria(BaseModel):
    criteria: List[ImportantCriterion] = Field(
        ..., description="List of IMPORTANT criteria"
    )

    @validator("criteria")
    def validate_criteria(cls, v):
        totalWeight = sum(criterion.weight for criterion in v)
        if not 0.99 <= totalWeight <= 1.01:
            raise ValueError(
                f"Sum of IMPORTANT criteria weights must be 1, got {totalWeight}"
            )
        return v


class NiceToHaveCriteria(BaseModel):
    criteria: List[NiceToHaveCriterion] = Field(
        ..., description="List of NICE_TO_HAVE criteria"
    )


class Scorecard(BaseModel):
    id: Optional[str] = Field(description="Unique identifier for the scorecard")
    jobOfferId: Optional[str] = Field(..., description="ID of the associated job offer")

    importantWeight: float = Field(
        description="Weight for the IMPORTANT section. Must be between 0 and 1 inclusive."
    )
    mustHaveWeight: float = Field(
        description="Weight for the MUST_HAVE section. Must be between 0 and 1 inclusive."
    )

    mustHaveCriteria: MustHaveCriteria = Field(..., description="MUST_HAVE criteria")
    importantCriteria: ImportantCriteria = Field(..., description="IMPORTANT criteria")
    niceToHaveCriteria: NiceToHaveCriteria = Field(
        ..., description="NICE_TO_HAVE criteria"
    )


class ScoredCriterion(BaseModel):
    id: str = Field(description="Unique identifier for the criterion")
    score: float = Field(description="Score assigned to this criterion")
    explanation: str = Field(description="Explanation for the assigned score")


class ListScoredCriterion(BaseModel):
    scoredCriteria: List[ScoredCriterion] = Field(description="List of scored criteria")


def load_scorecard_from_json(filePath: str) -> Scorecard:
    import json

    with open(filePath, "r") as file:
        data = json.load(file)
    return Scorecard.parse_obj(data)


def filter_criteria_by_type(
    scorecard: Scorecard, criteriaTypes: List[CriteriaType]
) -> List[Union[MustHaveCriterion, ImportantCriterion, NiceToHaveCriterion]]:
    filteredCriteria = []

    for criterion in (
        scorecard.mustHaveCriteria.criteria
        + scorecard.importantCriteria.criteria
        + scorecard.niceToHaveCriteria.criteria
    ):
        if criterion.type in criteriaTypes:
            filteredCriteria.append(criterion)

    return filteredCriteria
