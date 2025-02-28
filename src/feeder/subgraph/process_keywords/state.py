from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.raw_query import RawQuery
from src.feeder.subgraph.process_keywords.models.feedback_judge import (
    FeedbackResponse,
)


class KeywordsState(BaseModel):
    """State for keywords subgraph.

    Data Flow:
    1. job_offer_description: the job offer description JSON object
    2. json_object: the query JSON object
    3. feedback_judge: the feedback judge object
    """

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(...)
    feedback_judge: Optional[FeedbackResponse] = Field(None)


class KeywordsOutputState(BaseModel):
    """Output state for the new keywords subgraph."""

    json_object: RawQuery = Field(...)


class KeywordsInputState(BaseModel):
    """Input state for the keywords subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(...)
