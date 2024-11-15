import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from analysis.memory.models.company import CompanyInfo
from analysis.memory.models.school import SchoolInfo
from analysis.models.language import LanguageProficiency
from analysis.models.profile import Profile
from analysis.models.synthesis import (
    HierarchySynthesis,
    IntentSynthesis,
    LocationSynthesis,
    MustSynthesis,
    OpenToWorkSynthesis,
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

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]

    inferred_languages: Optional[List[LanguageProficiency]] = Field(default=None)
    inferred_sector: Optional[str] = Field(default=None)
    inferred_culture: Optional[str] = Field(default=None)

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]

    synthesis_location: Optional[LocationSynthesis] = Field(default=None)
    synthesis_must: Optional[MustSynthesis] = Field(default=None)
    synthesis_hierarchy: Optional[HierarchySynthesis] = Field(default=None)
    synthesis_open_to_work: Optional[OpenToWorkSynthesis] = Field(default=None)
    synthesis_intent: Optional[IntentSynthesis] = Field(default=None)
    synthesis_overall: Optional[Synthesis] = Field(default=None)
