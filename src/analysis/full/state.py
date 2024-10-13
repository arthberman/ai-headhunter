import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from candidate_matcher.analysis.models import ScoredCriterion
from candidate_matcher.career_path.models import CareerPathOutput
from analysis.models.company import CompanyInfo
from analysis.models.language import LanguageProficiency
from analysis.models.profile import (
    Profile,
    ProfileEducation,
    ProfileExperience,
)
from analysis.models.school import SchoolInfo
from candidate_matcher.synthesis.models import Synthesis
from scorecard.models.scorecard import Scorecard


class MainGraphState(BaseModel):
    """State of the main graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Annotated[List[LanguageProficiency], operator.add]

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    career_path: Optional[CareerPathOutput] = Field(default=None)
    synthesis: Optional[Synthesis] = Field(default=None)


class InputGraphState(BaseModel):
    """State of the input graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)


class EducationState(BaseModel):
    """State of the education graph."""

    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    """State of the experience graph."""

    experience: ProfileExperience = Field(...)
