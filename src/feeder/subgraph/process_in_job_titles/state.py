from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.raw_query import RawQuery
from src.feeder.subgraph.process_in_job_titles.models.feedback_judge import (
    FeedbackResponse,
)


class NewJobTitlesSubgraphInputState(BaseModel):
    """Input state for the new job titles subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: Optional[RawQuery] = Field(None)  # raw JSON object


class NewJobTitlesSubgraphState(BaseModel):
    """Pydantic object for the state of the new job titles subgraph.

    Data Flow:
    1. job_offer_description: the job offer description JSON object
    2. json_object: the query JSON object
    3. feedback_judge: the feedback judge object
    """

    job_offer_description: JobOfferDescription = Field(...)
    json_object: Optional[RawQuery] = Field(None)
    feedback_judge: Optional[FeedbackResponse] = Field(None)


class NewJobTitlesSubgraphOutputState(BaseModel):
    """Output state for the new job titles subgraph."""

    json_object: Optional[RawQuery] = Field(
        None
    )  # clean JSON object for "include" field
