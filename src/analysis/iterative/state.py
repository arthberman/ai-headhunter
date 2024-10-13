import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from analysis.models.company import CompanyInfo
from analysis.models.language import LanguageProficiency
from analysis.models.profile import (
    Profile,
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

    education_enrichment: List[SchoolInfo] = Field(...)
    experience_enrichment: List[CompanyInfo] = Field(...)
    language_enrichment: List[LanguageProficiency] = Field(...)


class MainGraphState(InputGraphState):
    """State of the main graph."""

    scored_criterion: Annotated[List[ScoredCriterion], operator.add]
    synthesis: Optional[Synthesis] = Field(default=None)
