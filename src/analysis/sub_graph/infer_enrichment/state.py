from typing import List

from pydantic import BaseModel, Field

from analysis.models.language import LanguageProficiency
from analysis.models.profile import Profile


class MainInferEnrichmentState(BaseModel):
    """State for the analysis graph."""

    profile: Profile = Field(...)


class OutputInferEnrichmentState(MainInferEnrichmentState):
    """Output state for the enrichment subgraph."""

    sector_analysis: str = Field(default=None)
    culture_analysis: str = Field(default=None)
    intent_analysis: str = Field(default=None)
    language_analysis: List[LanguageProficiency] = Field(default=None)
