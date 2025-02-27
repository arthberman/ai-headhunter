from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class FilterBase(BaseModel):
    """Base class for LinkedIn Recruiter filters."""

    id: Optional[str] = Field(
        default=None, description="Unique identifier for the filter."
    )
    required: bool = Field(default=True, description="Whether the filter is required.")
    negative: bool = Field(
        default=False, description="Whether to include or not include in the filters."
    )


class TitleFilter(FilterBase):
    """Model for LinkedIn Recruiter title filters."""

    scope: Literal["CURRENT_OR_PAST", "CURRENT", "PAST", "PAST NOT CURRENT"] = Field(
        default="CURRENT", description="Scope of the title filter."
    )
    text: str = Field(..., description="Title to filter by.")


class LocationFilter(FilterBase):
    """Model for LinkedIn Recruiter location filters."""

    scope: Literal[
        "CURRENT", "OPEN_TO_RELOCATE_ONLY", "CURRENT_OR_OPEN_TO_RELOCATE"
    ] = Field(default="CURRENT", description="Scope of the location filter.")
    title: Optional[str] = Field("", description="Title to filter by.")


class SeniorityEnum(str, Enum):
    """Enum for LinkedIn Recruiter seniority levels."""

    entry = "Entry"
    senior = "Senior"
    manager = "Manager"
    director = "Director"
    owner = "Owner"
    vp = "VP"
    cxo = "CXO"
    training = "Training"
    unpaid = "Unpaid"
    partner = "Partner"


class YearsOfExperienceFilter(BaseModel):
    """Model for LinkedIn Recruiter years of experience filters."""

    min: int = Field(..., description="Minimum years of experience.")
    max: int = Field(..., description="Maximum years of experience.")


class LinkedinRecruiterFilter(BaseModel):
    """Model for LinkedIn Recruiter filters."""

    TITLES: Optional[list[TitleFilter]] = Field(
        default=None, description="Title filters."
    )
    KEYWORDS: Optional[str] = Field(default=None, description="Keywords to filter by.")
    BING_GEO_SWR: Optional[list[LocationFilter]] = Field(
        default=None, description="Location filters."
    )
    TOTAL_YEARS_OF_EXPERIENCE_RANGE: Optional[YearsOfExperienceFilter] = Field(
        default=None, description="Years of experience filters."
    )
