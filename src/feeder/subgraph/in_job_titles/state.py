from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.raw_query import RawQuery
from feeder.subgraph.in_job_titles.models.feedback_judge import (
    FeedbackResponse,
)


class NewJobTitlesSubgraphState(BaseModel):
    """State for the new job titles subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: Optional[RawQuery] = Field(None)
    feedback_judge: Optional[FeedbackResponse] = Field(None)


class NewJobTitlesSubgraphOutputState(BaseModel):
    """Output state for the new job titles subgraph."""

    json_object: Optional[RawQuery] = Field(None)


class NewJobTitlesSubgraphInputState(BaseModel):
    job_offer_description: JobOfferDescription = Field(...)
    json_object: Optional[RawQuery] = Field(None)
