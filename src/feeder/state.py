import operator
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from feeder.models.filters_query import FilterQueryList
from feeder.models.job_offer import JobOfferDescription
from feeder.models.job_titles_ranking import (
    JobTitlesRankings,
)
from feeder.models.query_memory import QueryMemory
from feeder.models.raw_query import RawQuery
from feeder.models.keywords_ranking import (
    KeywordsRankings,
)

# from feeder.models.keywords import Keyword
from feeder.models.location import LocationList
from feeder.models.seniority_level import SeniorityLevel


class OverallState(BaseModel):
    """State model containing job offer details and derived search parameters."""

    job_offer_description: JobOfferDescription = Field(...)

    json_object: Optional[RawQuery] = Field(None)

    # focus on seniority level
    seniority_level: Optional[SeniorityLevel] = Field(None)

    # focus on job title
    real_job_title: Optional[str] = Field(None)

    keywords: Optional[List[str]] = Field(None)

    locations: Optional[LocationList] = Field(None)
    include: Optional[List[str]] = Field(None)
    exclude: Optional[List[str]] = Field(None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    job_titles_classified: Optional[JobTitlesRankings] = Field(None)
    keywords_classified: Optional[dict] = Field(None)
    query_results: Optional[FilterQueryList] = Field(None)
    current_query_index: Optional[int] = Field(default=0)
    query_memory: Optional[QueryMemory] = Field(None)
    global_iteration_count: int = Field(
        default=0, description="Counter for global feedback iterations"
    )


class OverallInputState(BaseModel):
    """Input state model containing job offer description."""

    job_offer_description: JobOfferDescription = Field(...)


class OverallOutputState(BaseModel):
    """Output state model containing Sales Navigator queries and search parameters."""

    locations: Optional[LocationList] = Field(None)
    seniority_level: Optional[SeniorityLevel] = Field(None)
    job_titles_classified: Optional[JobTitlesRankings] = Field(None)
    keywords_classified: Optional[KeywordsRankings] = Field(None)
