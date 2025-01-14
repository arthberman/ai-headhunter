from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.raw_query import RawQuery
from feeder.subgraph.not_in_job_titles.models.feedback_judge import (
    FeedbackResponse,
)


class JobsToExcludeState(BaseModel):
    """State for the new not in job titles subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(None)
    feedback_judge: Optional[FeedbackResponse] = Field(None)


class JobsToExcludeOutputState(BaseModel):
    """Output state for the new not in job titles subgraph."""

    json_object: RawQuery


class JobsToExcludeInputState(BaseModel):
    """Input state for the jobs to exclude subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(None)
