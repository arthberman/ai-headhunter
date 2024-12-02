from typing import List

from pydantic import BaseModel, Field

from analysis.models.language import LanguageProficiency
from analysis.models.profile import Profile


class MainInferEnrichmentState(BaseModel):
    """State for the analysis graph."""

    profile: Profile = Field(...)


class OutputInferEnrichmentState(MainInferEnrichmentState):
    """Output state for the enrichment subgraph."""

    inferred_industry_sector: str = Field(default=None)
    inferred_culture: str = Field(default=None)
    inferred_languages: List[LanguageProficiency] = Field(default=None)
    inferred_role_trajectory: str = Field(default=None)
