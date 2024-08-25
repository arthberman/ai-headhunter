import operator
from typing import Annotated, List, Optional

from langchain.pydantic_v1 import BaseModel, Field

from matcher.models.career_path import CareerPathAnalysis
from matcher.models.company import CompanyInfo
from matcher.models.job_offer import JobOffer
from matcher.models.language import LanguageProficiency
from matcher.models.profile import Profile, ProfileEducation, ProfileExperience
from matcher.models.school import SchoolInfo
from matcher.models.scorecard import Scorecard, ListScoredCriterion


class MainGraphState(BaseModel):
    profile: Profile = Field(...)
    job_offer: JobOffer = Field(...)
    scorecard: Scorecard = Field(...)
    analysisId: str = Field(...)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Optional[List[LanguageProficiency]] = Field(
        default_factory=list
    )

    career_path_analysis: Optional[CareerPathAnalysis]
    education_analysis: Optional[ListScoredCriterion]
    experience_analysis: Optional[ListScoredCriterion]
    soft_skill_analysis: Optional[ListScoredCriterion]
    hard_skill_analysis: Optional[ListScoredCriterion]
    language_analysis: Optional[ListScoredCriterion]

    must_have_score: Optional[float] = Field(default=None, ge=0, le=1)
    important_score: Optional[float] = Field(default=None, ge=0, le=1)
    nice_to_have_multiplier: Optional[float] = Field(default=None, g=0, l=2)
    final_score: Optional[float] = Field(default=None, ge=0, le=1)


class EducationState(BaseModel):
    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    experience: ProfileExperience = Field(...)
