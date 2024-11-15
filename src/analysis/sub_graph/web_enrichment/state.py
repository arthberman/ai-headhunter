import operator
from typing import Annotated, List

from langgraph.store.base import Op
from pydantic import BaseModel, Field

from analysis.memory.models.company import CompanyInfo
from analysis.memory.models.school import SchoolInfo
from analysis.models.profile import Profile, ProfileEducation, ProfileExperience


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


class MainEnrichmentState(OutputEnrichmentState):
    """State for the analysis graph."""

    profile: Profile = Field(...)

    batch_store_ops: Annotated[List[Op], operator.add] = Field(default_factory=list)
