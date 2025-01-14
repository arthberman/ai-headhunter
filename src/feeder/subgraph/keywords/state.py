from typing import Optional

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.raw_query import RawQuery
from feeder.subgraph.keywords.models.feedback_judge import FeedbackResponse


class KeywordsState(BaseModel):
    """State for the new keywords subgraph."""

    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(None)
    feedback_judge: Optional[FeedbackResponse] = Field(None)


class KeywordsOutputState(BaseModel):
    """Output state for the new keywords subgraph."""

    json_object: RawQuery = Field(None)


class KeywordsInputState(BaseModel):
    job_offer_description: JobOfferDescription = Field(...)
    json_object: RawQuery = Field(None)
