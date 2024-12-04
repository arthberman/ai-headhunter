from typing import List

from pydantic import BaseModel, Field

from matcher.models.language import LanguageProficiency
from matcher.models.profile import Profile


class MainInferEnrichmentState(BaseModel):
    """State for the matcher graph."""

    profile: Profile = Field(...)


class OutputInferEnrichmentState(MainInferEnrichmentState):
    """Output state for the enrichment subgraph."""

    inferred_industry_sector: str = Field(default=None)
    inferred_culture: str = Field(default=None)
    inferred_languages: List[LanguageProficiency] = Field(default=None)
    inferred_role_trajectory: str = Field(default=None)
