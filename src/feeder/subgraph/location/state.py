from typing import List, Optional, Tuple

from pydantic import BaseModel, Field

from feeder.models.job_offer import JobOfferDescription
from feeder.models.location import LocationList


class LocationSubGraphState(BaseModel):
    # private keys
    job_location: Optional[str] = Field(None)
    api_out_locations: Optional[List[Tuple[str, str]]] = Field(None)

    # shared with OverallState
    job_offer_description: JobOfferDescription = Field(...)
    locations: Optional[LocationList] = Field(None)


class LocationOutputState(BaseModel):
    locations: Optional[LocationList] = Field(None)


class LocationSubGraphInputState(BaseModel):
    job_offer_description: JobOfferDescription = Field(...)
