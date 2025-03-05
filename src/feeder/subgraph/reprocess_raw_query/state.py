from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.raw_query import RawQuery


class ReprocessRawQueryInputState(BaseModel):
    """Input state for separate raw query subgraph."""

    json_object: RawQuery


class ReprocessRawQueryState(ReprocessRawQueryInputState):
    """State for reprocess raw query."""

    in_job_titles: Optional[list[str]] = Field(
        ...,
        description="List of job titles that are relevant to include in a LinkedIn Sales Navigator search to find perfect candidates given a job offer description",
    )
    not_in_job_titles: Optional[list[str]] = Field(
        ...,
        description="List of seniority indicators or precise job titles that must be excluded from a LinkedIn Sales Navigator search given a job offer description",
    )
    keywords: Optional[list[str]] = Field(
        ...,
        description="List of keywords to find perfect candidates based on a given job offer description",
    )


class ReprocessRawQueryOutputState(BaseModel):
    """Output state for separate raw query subgraph."""

    json_object: RawQuery
