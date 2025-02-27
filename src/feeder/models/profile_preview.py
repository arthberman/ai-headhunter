from typing import Annotated, List, Optional

from pydantic import BaseModel, BeforeValidator, Field, HttpUrl


# Helper function to parse display count string
def parse_display_count(val: str | int) -> int:
    """Parse display count string."""
    if isinstance(val, str):
        if val.endswith("K+"):
            return int(float(val[:-2]) * 1000)
        return int(val)
    else:
        return val


ParseDisplayCount = Annotated[int, BeforeValidator(parse_display_count)]


class ProfilePreview(BaseModel):
    """Represents a preview of a LinkedIn profile."""

    linkedin_profile_url: HttpUrl = Field(
        ..., description="URL of the LinkedIn profile."
    )
    linkedin_profile_urn: str = Field(..., description="URN of the LinkedIn profile.")
    name: Optional[str] = Field(None, description="Name of the person.")
    location: Optional[str] = Field(None, description="Location of the person.")
    default_position_title: Optional[str] = Field(
        None, description="Default position title."
    )
    default_position_company_id: Optional[str] = Field(
        None, description="Default position company."
    )


class ProfilesPreviewResponse(BaseModel):
    """Response structure for for crust API profiel search."""

    profiles: List[ProfilePreview] = Field(..., description="List of profiles.")
    total_display_count: ParseDisplayCount = Field(
        ..., description="Total display count of profiles."
    )
