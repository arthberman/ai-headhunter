from typing import List

from pydantic import BaseModel, Field

from analysis.models.company import CompanyInfo
from analysis.models.language import LanguageProficiency
from analysis.models.profile import (
    Profile,
)
from analysis.models.school import SchoolInfo
from scorecard.models.scorecard import Scorecard


class InputGraphState(BaseModel):
    """State of the input graph."""

    profile: Profile = Field(...)
    scorecard: Scorecard = Field(...)
    job_synthesis: str = Field(...)

    education_enrichment: List[SchoolInfo] = Field(...)
    experience_enrichment: List[CompanyInfo] = Field(...)
    infer_languages: List[LanguageProficiency] = Field(...)
    infer_sector: str = Field(...)
    infer_culture: str = Field(...)
