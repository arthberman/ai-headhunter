import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from analysis.models.company import CompanyInfo
from analysis.models.language import LanguageProficiency
from analysis.models.location import ScoredLocationCriterion
from analysis.models.profile import Profile
from analysis.models.school import SchoolInfo
from analysis.models.synthesis import Synthesis
from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
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

    infer_languages: Optional[List[LanguageProficiency]] = Field(default=None)
    infer_sector: Optional[str] = Field(default=None)
    infer_culture: Optional[str] = Field(default=None)
    infer_intent: Optional[str] = Field(default=None)

    hierarchy_analysis: Optional[str] = Field(default=None)

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    scored_location_criterion: Optional[ScoredLocationCriterion] = Field(default=None)

    synthesis: Optional[Synthesis] = Field(default=None)
