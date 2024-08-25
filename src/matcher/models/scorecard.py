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


class Criterion(BaseModel):
    id: Optional[str] = Field(description="Unique identifier for the criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    type: CriteriaType = Field(..., description="Type of the criterion")
    weight: Optional[float] = Field(
        gt=0,
        le=1,
        description="Weight of the criterion (required for MUST_HAVE and IMPORTANT)",
    )
    compensationDescription: Optional[str] = Field(
        description="Description of how compensation is applied (required for MUST_HAVE)",
    )
    compensationScore: Optional[float] = Field(
        ge=0,
        le=1,
        description="Score applied for compensation (required for MUST_HAVE)",
    )
    maxBonusPoint: Optional[float] = Field(
        ge=0,
        description="Maximum bonus points for this criterion (required for NICE_TO_HAVE)",
    )


class ScorecardSection(BaseModel):
    importanceLevel: ImportanceLevel = Field(
        ..., description="Importance level of the section"
    )
    criteria: List[Criterion] = Field(
        ..., description="List of criteria in this section"
    )

    @validator("criteria")
    def validate_criteria(cls, v, values):
        importanceLevel = values.get("importanceLevel")
        if importanceLevel in [ImportanceLevel.MUST_HAVE, ImportanceLevel.IMPORTANT]:
            for criterion in v:
                if criterion.weight is None:
                    raise ValueError(
                        f"Weight is required for criteria in {importanceLevel} section"
                    )
            totalWeight = sum(criterion.weight for criterion in v)
            if not 0.99 <= totalWeight <= 1.01:
                raise ValueError(
                    f"Sum of criteria weights within {importanceLevel} section must be 1, got {totalWeight}"
                )
        elif importanceLevel == ImportanceLevel.NICE_TO_HAVE:
            for criterion in v:
                if criterion.maxBonusPoint is None:
                    raise ValueError(
                        "maxBonusPoint is required for criteria in NICE_TO_HAVE section"
                    )
        return v


class Scorecard(BaseModel):
    id: Optional[str] = Field(description="Unique identifier for the scorecard")
    jobOfferId: Optional[str] = Field(..., description="ID of the associated job offer")

    importantWeight: float = Field(
        0.3, ge=0, le=1, description="Weight for the IMPORTANT section"
    )
    mustHaveWeight: float = Field(
        0.7, ge=0, le=1, description="Weight for the MUST_HAVE section"
    )

    sections: List[ScorecardSection] = Field(
        ..., description="List of sections in the scorecard"
    )

    @validator("sections")
    def validate_sections(cls, v):
        importanceLevels = [section.importanceLevel for section in v]
        requiredLevels = set(ImportanceLevel)
        if not requiredLevels.issubset(set(importanceLevels)):
            missingLevels = requiredLevels - set(importanceLevels)
            raise ValueError(
                f"Scorecard is missing sections: {', '.join(missingLevels)}"
            )
        return v


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
) -> List[Criterion]:
    filteredCriteria = []

    for section in scorecard.sections:
        for criterion in section.criteria:
            if criterion.type in criteriaTypes:
                filteredCriteria.append(criterion)

    return filteredCriteria
