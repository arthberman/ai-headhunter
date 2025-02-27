from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_titles_ranking import JobTitlesRankings
from feeder.models.keywords_ranking import KeywordsRankings
from feeder.models.location import LocationData
from feeder.models.raw_query import RawQuery

from .models.linkedin_recruiter_filters import LinkedinRecruiterFilter


class LinkedinRecruiterState(BaseModel):
    """State of the linkedin recruiter subgraph."""

    query_results: list[LinkedinRecruiterFilter] = Field(
        ..., description="Query results."
    )
    job_titles_classified: JobTitlesRankings = Field(
        ..., description="Classified job titles."
    )
    json_object: RawQuery = Field(..., description="Raw query object.")
    locations: LocationData = Field(..., description="Location data.")
    keywords_classified: Optional[KeywordsRankings] = Field(
        ..., description="Classified keywords."
    )
