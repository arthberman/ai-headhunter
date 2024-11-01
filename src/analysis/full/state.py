import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from analysis.models.company import CompanyInfo
from analysis.models.language import LanguageProficiency
from analysis.models.profile import (
    Profile,
    ProfileEducation,
    ProfileExperience,
)
from analysis.models.school import SchoolInfo
from analysis.models.synthesis import Synthesis
from analysis.nodes.analysis_subgraph.models import ScoredCriterion
from scorecard.models.scorecard import Scorecard


class InputGraphState(BaseModel):
    """State of the input graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)


class MainGraphState(InputGraphState):
    """State of the main graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]
    language_enrichment: Optional[List[LanguageProficiency]] = Field(default=None)

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    sector_analysis: Optional[str] = Field(default=None)
    culture_analysis: Optional[str] = Field(default=None)
    intent_analysis: Optional[str] = Field(default=None)
    hierarchy_analysis: Optional[str] = Field(default=None)
    synthesis: Optional[Synthesis] = Field(default=None)


class EducationState(BaseModel):
    """State of the education graph."""

    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    """State of the experience graph."""

    experience: ProfileExperience = Field(...)
