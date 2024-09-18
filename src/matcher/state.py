import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from matcher.models.career_path import CareerPathAnalysis
from matcher.models.company import CompanyInfo
from matcher.models.job_posting import JobPosting
from matcher.models.language import LanguageProficiency
from matcher.models.profile import Profile, ProfileEducation, ProfileExperience
from matcher.models.school import SchoolInfo
from scorecard.models.scorecard import Scorecard, ListScoredCriterion


class MainGraphState(BaseModel):
    profile: Profile = Field(...)
    jobPosting: JobPosting = Field(...)
    scorecard: Scorecard = Field(...)
    analysisId: Optional[str] = Field(default=None)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Optional[List[LanguageProficiency]] = Field(
        default_factory=list
    )


class InputGraphState(BaseModel):
    profile: Profile = Field(...)
    jobPosting: JobPosting = Field(...)
    scorecard: Scorecard = Field(...)


class EducationState(BaseModel):
    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    experience: ProfileExperience = Field(...)
