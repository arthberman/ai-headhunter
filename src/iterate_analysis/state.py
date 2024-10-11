import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, Field

from iterate_analysis.analysis.models import ScoredCriterion
from iterate_analysis.synthesis.models import Synthesis
from models.analysis.company import CompanyInfo
from models.analysis.language import LanguageProficiency
from models.analysis.profile import (
    Profile,
)
from models.analysis.school import SchoolInfo
from models.scorecard.scorecard import Scorecard


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
