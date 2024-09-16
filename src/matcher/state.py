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

    career_path_analysis: Optional[CareerPathAnalysis] = None
    education_analysis: Optional[ListScoredCriterion] = None
    experience_analysis: Optional[ListScoredCriterion] = None
    soft_skill_analysis: Optional[ListScoredCriterion] = None
    hard_skill_analysis: Optional[ListScoredCriterion] = None
    language_analysis: Optional[ListScoredCriterion] = None
    industry_knowledge_analysis: Optional[ListScoredCriterion] = None
    additional_qualification_analysis: Optional[ListScoredCriterion] = None

    must_have_score: Optional[float] = Field(default=None, ge=0, le=1)
    important_score: Optional[float] = Field(default=None, ge=0, le=1)
    nice_to_have_multiplier: Optional[float] = Field(default=None, g=0, l=2)
    final_score: Optional[float] = Field(default=None, ge=0, le=1)


class EducationState(BaseModel):
    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    experience: ProfileExperience = Field(...)
