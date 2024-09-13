from enum import Enum
from typing import Dict, List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field


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


class ScoringDistribution(str, Enum):
    BINARY = "BINARY"
    CONTINUOUS = "CONTINUOUS"
    ORDINAL = "ORDINAL"
    GAUSSIAN = "GAUSSIAN"


class BaseCriterion(BaseModel):
    id: Optional[str] = Field(description="Unique identifier for the criterion")
    description: str = Field(..., description="Detailed description of the criterion")
    type: CriteriaType = Field(
        ...,
        description="Type of the criterion (EDUCATION, EXPERIENCE, LANGUAGE, HARD_SKILL, SOFT_SKILL, INDUSTRY_KNOWLEDGE, ADDITIONAL_QUALIFICATION)",
    )
    context: Optional[str] = Field(
        description="This is the context of the job posting that is relevant to the criterion (definition of the scope).",
    )
    scoring_distribution: ScoringDistribution = Field(
        ...,
        description="The type of scoring distribution for this criterion",
    )
    distribution_params: Optional[Dict[str, float]] = Field(
        description="Parameters specific to the chosen scoring distribution",
    )


class Scorecard(BaseModel):
    context: Optional[str] = Field(
        description="Global context of the scorecard.",
    )
    mustHaveCriteria: List[BaseCriterion] = Field(..., description="MUST_HAVE criteria")
    importantCriteria: List[BaseCriterion] = Field(
        ..., description="IMPORTANT criteria"
    )
    niceToHaveCriteria: List[BaseCriterion] = Field(
        ..., description="NICE_TO_HAVE criteria"
    )


class ScoredCriterion(BaseModel):
    id: str = Field(..., description="Unique identifier for the criterion")
    score: float = Field(
        ..., ge=0, le=1, description="Score assigned to this criterion"
    )
    explanation: str = Field(..., description="Explanation for the assigned score")
    confidence_level: float = Field(
        ..., ge=0, le=1, description="Confidence level in the assigned score (0 to 1)"
    )


class ListScoredCriterion(BaseModel):
    scoredCriteria: List[ScoredCriterion] = Field(description="List of scored criteria")


def load_scorecard_from_json(filePath: str) -> Scorecard:
    import json

    with open(filePath, "r") as file:
        data = json.load(file)
    return Scorecard.parse_obj(data)


def filter_criteria_by_type(
    scorecard: Scorecard, criteriaTypes: List[CriteriaType]
) -> List[BaseCriterion]:
    filteredCriteria = []

    for importance, criteria_list in [
        (ImportanceLevel.MUST_HAVE, scorecard.mustHaveCriteria),
        (ImportanceLevel.IMPORTANT, scorecard.importantCriteria),
        (ImportanceLevel.NICE_TO_HAVE, scorecard.niceToHaveCriteria),
    ]:
        for criterion in criteria_list:
            if criterion.type in criteriaTypes:
                criterion.importance = importance
                filteredCriteria.append(criterion)

    return filteredCriteria
