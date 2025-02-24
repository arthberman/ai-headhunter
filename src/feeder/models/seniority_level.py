from enum import Enum

from pydantic import BaseModel, Field


class SeniorityEnum(str, Enum):
    """Enum for seniority levels."""

    LESSTHANAYEAR = ("Less than 1 year", 1)
    ONE_TO_TWO_YEARS = ("1 to 2 years", 2)
    THREE_TO_FIVE_YEARS = ("3 to 5 years", 3)
    SIX_TO_TEN_YEARS = ("6 to 10 years", 4)
    MORETHANTENYEARS = ("More than 10 years", 5)

    def __new__(cls, label: str, id: int):
        """Create a new seniority level enum."""
        obj = str.__new__(cls, label)
        obj._value_ = label
        return obj
    
    def get_range(self) -> tuple:
        """Get the years of experience range for the seniority level.

        Returns: (min, max) years of experience range
        """
        if self == SeniorityEnum.LESSTHANAYEAR:
            return (0, 1)
        elif self == SeniorityEnum.ONE_TO_TWO_YEARS:
            return (1, 2)
        elif self == SeniorityEnum.THREE_TO_FIVE_YEARS:
            return (3, 5)
        elif self == SeniorityEnum.SIX_TO_TEN_YEARS:
            return (6, 10)
        elif self == SeniorityEnum.MORETHANTENYEARS:
            return (10, 100)
        else:
            return None, None
class LinkedInExperienceRange(BaseModel):
    """Enum for LinkedIn experience ranges."""

    id: str
    label: str


class YearsExperience(BaseModel):
    """Years of experience.

    Attributes:
        min: Minimum years of experience
        max: Maximum years of experience
    """

    min: int = Field(description="Minimum years of experience")
    max: int = Field(description="Maximum years of experience")

    def to_linkedin_range(self) -> list[LinkedInExperienceRange]:
        """Convert years of experience to LinkedIn experience ranges.

        Returns:
            List of LinkedIn experience ranges
        """
        ranges = []

        # Add applicable ranges based on min and max years
        if self.min <= 1:
            ranges.append(LinkedInExperienceRange(id="1", label="Less than 1 year"))
        if self.max >= 1 and self.min <= 2:
            ranges.append(LinkedInExperienceRange(id="2", label="1 to 2 years"))
        if self.max >= 3 and self.min <= 5:
            ranges.append(LinkedInExperienceRange(id="3", label="3 to 5 years"))
        if self.max >= 6 and self.min <= 10:
            ranges.append(LinkedInExperienceRange(id="4", label="6 to 10 years"))
        # if self.max > 10:
        #     ranges.append(LinkedInExperienceRange(id="5", label="Plus de 10 ans"))

        return ranges


class SeniorityLevel(BaseModel):
    """Seniority level.

    Attributes:
        seniority_level: Seniority level
        years_experience: Years of experience
    """

    seniority_level: SeniorityEnum = Field(
        description="Required seniority level for the position"
    )
    years_experience: YearsExperience = Field(
        description="Recommended years of experience range"
    )
