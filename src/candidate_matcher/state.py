import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from candidate_matcher.analysis.models import ScoredCriterion
from candidate_matcher.career_path.models import CareerPathOutput
from candidate_matcher.models.company import CompanyInfo
from candidate_matcher.models.language import LanguageProficiency
from candidate_matcher.models.profile import (
    Profile,
    ProfileEducation,
    ProfileExperience,
)
from candidate_matcher.models.school import SchoolInfo
from candidate_matcher.synthesis.models import Synthesis
from scorecard_generator.models.scorecard import Scorecard


class MainGraphState(BaseModel):
    """State of the main graph."""

    profile: Optional[Profile] = Field(default=None)
    # jobPosting: JobPosting = Field(...)
    scorecard: Optional[Scorecard] = Field(default=None)
    job_synthesis: Optional[str] = Field(default=None)
    analysis_id: Optional[str] = Field(default=None)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Optional[List[LanguageProficiency]] = Field(
        default_factory=list
    )

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    career_path: Optional[CareerPathOutput] = Field(default=None)
    synthesis: Optional[Synthesis] = Field(default=None)


class InputGraphState(BaseModel):
    """State of the input graph."""

    analysis_id: Optional[str] = Field(default=None)
    profile: Optional[Profile] = Field(default=None)
    scorecard: Optional[Scorecard] = Field(default=None)
    job_synthesis: Optional[str] = Field(default=None)


class EducationState(BaseModel):
    """State of the education graph."""

    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    """State of the experience graph."""

    experience: ProfileExperience = Field(...)
