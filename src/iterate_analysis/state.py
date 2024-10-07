import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from iterate_analysis.analysis.models import ScoredCriterion
from iterate_analysis.models.company import CompanyInfo
from iterate_analysis.models.language import LanguageProficiency
from iterate_analysis.models.profile import (
    Profile,
    ProfileEducation,
    ProfileExperience,
)
from iterate_analysis.models.school import SchoolInfo
from iterate_analysis.synthesis.models import Synthesis
from scorecard_generator.models.scorecard import Scorecard


class MainGraphState(BaseModel):
    """State of the main graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Annotated[List[LanguageProficiency], operator.add]

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    synthesis: Optional[Synthesis] = Field(default=None)


class InputGraphState(BaseModel):
    """State of the input graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)
    education_enrichment: List[SchoolInfo] = Field(...)
    experience_enrichment: List[CompanyInfo] = Field(...)
    language_enrichment: List[LanguageProficiency] = Field(...)


class EducationState(BaseModel):
    """State of the education graph."""

    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    """State of the experience graph."""

    experience: ProfileExperience = Field(...)
