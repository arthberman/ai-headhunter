from typing import List

from pydantic import BaseModel, Field


class LocationItem(BaseModel):
    """Represents a single location item with an identifier."""

    id: str = Field(description="Unique identifier for the location")
    name: str = Field(description="The name/string representation of the location")


class LocationData(BaseModel):
    """Container for list of LocationItems."""

    items: List[LocationItem] = Field(
        description="List of location items containing id and name pairs"
    )
