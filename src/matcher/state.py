import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from matcher.analysis.models import ScoredCriterion
from matcher.models.company import CompanyInfo
from matcher.models.language import LanguageProficiency
from matcher.models.profile import Profile, ProfileEducation, ProfileExperience
from matcher.models.school import SchoolInfo
from matcher.synthesis.models import Synthesis
from scorecard.models.scorecard import Scorecard


class MainGraphState(BaseModel):
    profile: Optional[Profile] = Field(default=None)
    # jobPosting: JobPosting = Field(...)
    scorecard: Optional[Scorecard] = Field(default=None)
    scorecard_synthesis: Optional[str] = Field(default=None)
    analysisId: Optional[str] = Field(default=None)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Optional[List[LanguageProficiency]] = Field(
        default_factory=list
    )

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    synthesis: Optional[Synthesis] = Field(default=None)


class InputGraphState(BaseModel):
    analysisId: Optional[str] = Field(default=None)


class EducationState(BaseModel):
    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    experience: ProfileExperience = Field(...)
