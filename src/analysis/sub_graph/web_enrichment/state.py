import operator
from typing import Annotated, List

from pydantic import BaseModel, Field

from analysis.models.profile import Profile, ProfileEducation, ProfileExperience
from memory_graph.models import CompanyInfo, SchoolInfo


class MainEnrichmentState(BaseModel):
    """State for the analysis graph."""

    profile: Profile = Field(...)


class OutputEnrichmentState(BaseModel):
    """Output state for the enrichment subgraph."""

    education_enrichment: Annotated[List[SchoolInfo], operator.add]
    experience_enrichment: Annotated[List[CompanyInfo], operator.add]


class EducationState(BaseModel):
    """State of the education graph."""

    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    """State of the experience graph."""

    experience: ProfileExperience = Field(...)
