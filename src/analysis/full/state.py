import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from analysis.models.company import CompanyInfo
from analysis.models.language import LanguageProficiency
from analysis.models.profile import Profile
from analysis.models.school import SchoolInfo
from analysis.models.synthesis import (
    CultureSynthesis,
    HierarchySynthesis,
    IntentSynthesis,
    LocationSynthesis,
    MustSynthesis,
    NiceSynthesis,
    Synthesis,
)
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

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]

    synthesis_must: Optional[MustSynthesis] = Field(default=None)
    synthesis_nice: Optional[NiceSynthesis] = Field(default=None)
    synthesis_culture: Optional[CultureSynthesis] = Field(default=None)
    synthesis_intent: Optional[IntentSynthesis] = Field(default=None)
    synthesis_hierarchy: Optional[HierarchySynthesis] = Field(default=None)
    synthesis_location: Optional[LocationSynthesis] = Field(default=None)
    synthesis_overall: Optional[Synthesis] = Field(default=None)
