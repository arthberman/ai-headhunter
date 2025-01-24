from typing import List, Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    """Location of the job offer."""

    name: str = Field(
        description="The name/string representation of the location (e.g. 'Paris, France')"
    )


class LocationItem(BaseModel):
    """Represents a single location item with an identifier."""

    id: str = Field(description="Unique identifier for the location")
    name: str = Field(description="The name/string representation of the location")


class LocationData(BaseModel):
    """Container for location items."""

    items: List[LocationItem] = Field(
        description="List of location items containing id and name pairs"
    )


class LocationAPIResponse(BaseModel):
    """API response wrapper for location data."""

    success: bool = Field(description="Indicates if the API request was successful")
    message: str = Field(
        description="Response message providing additional context about the request result"
    )
    data: Optional[LocationData] = Field(
        default=None,
        description="Optional location data returned when the request is successful",
    )


class LocationList(BaseModel):
    """A list of locations and their ids generated from the job offer description."""

    locations: List[LocationItem] = Field(
        description="A list of locations and their ids generated from the job offer description."
    )
