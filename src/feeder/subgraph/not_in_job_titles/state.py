from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.raw_query import RawQuery
from src.feeder.subgraph.not_in_job_titles.models.feedback_judge import (
    FeedbackResponse,
)


class JobsToExcludeState(BaseModel):
    """Pydantic object for the state of the jobs to exclude subgraph.

    Data Flow:
    1. job_offer_description: the job offer description JSON object
    2. json_object: the query JSON object
    3. feedback_judge: the feedback judge object
    """

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(None)
    feedback_judge: Optional[FeedbackResponse] = Field(None)


class JobsToExcludeInputState(BaseModel):
    """Input state for the jobs to exclude subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(None)


class JobsToExcludeOutputState(BaseModel):
    """Output state for the new not in job titles subgraph."""

    json_object: RawQuery
