from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.location import LocationItem


class LocationSubGraphState(BaseModel):
    """Pydantic object for the state of the location processing pipeline.

    Data Flow:
    1. job_location: extracted from job description by LLM
    2. api_out_locations: raw location pairs from API/cache lookup
    3. locations: final processed location list for search
    """

    # private keys (used only within location subgraph)
    job_location: Optional[str] = Field(None)
    api_out_locations: Optional[List[Tuple[str, str]]] = Field(
        None
    )  # [(id, name), ...]

    # shared with OverallState (passed between graphs)
    job_offer_description: JobOfferDescription = Field(...)
    locations: Optional[List[LocationItem]] = Field(None)


class LocationSubGraphInputState(BaseModel):
    """Input state for location subgraph."""

    job_offer_description: JobOfferDescription = Field(...)


class LocationOutputState(BaseModel):
    """Output state for location subgraph."""

    locations: Optional[List[LocationItem]] = Field(None)
