import operator
from typing import Annotated, List

from langgraph.store.base import Op
from pydantic import BaseModel, Field

from matcher.memory.models.company import CompanyInfo
from matcher.memory.models.school import SchoolInfo
from matcher.models.profile import Profile, ProfileEducation, ProfileExperience
from utils import reducer_list


class OutputEnrichmentState(BaseModel):
    """Output state for the enrichment subgraph."""

    education_enrichment: Annotated[List[SchoolInfo], operator.add] = Field(
        default_factory=list
    )
    experience_enrichment: Annotated[List[CompanyInfo], operator.add] = Field(
        default_factory=list
    )


class EducationState(BaseModel):
    """State of the education graph."""

    education: ProfileEducation = Field(...)


class ExperienceState(BaseModel):
    """State of the experience graph."""

    experience: ProfileExperience = Field(...)


class MainEnrichmentState(OutputEnrichmentState):
    """State for the matcher graph."""

    profile: Profile = Field(...)

    batch_store_ops: Annotated[List[Op], reducer_list] = Field(default_factory=list)
