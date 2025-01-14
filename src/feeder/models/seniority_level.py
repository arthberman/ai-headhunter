from enum import Enum

from pydantic import BaseModel, Field


class SeniorityEnum(str, Enum):
    LESSTHANAYEAR = ("Less than 1 year", 1)
    ONE_TO_TWO_YEARS = ("1 to 2 years", 2)
    THREE_TO_FIVE_YEARS = ("3 to 5 years", 3)
    SIX_TO_TEN_YEARS = ("6 to 10 years", 4)
    MORETHANTENYEARS = ("More than 10 years", 5)

    def __new__(cls, label: str, id: int):
        obj = str.__new__(cls, label)
        obj._value_ = label
        obj.id = id
        return obj


class LinkedInExperienceRange(BaseModel):
    id: str
    label: str


class YearsExperience(BaseModel):
    min: int = Field(description="Minimum years of experience")
    max: int = Field(description="Maximum years of experience")

    def to_linkedin_range(self) -> list[LinkedInExperienceRange]:
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
    seniority_level: SeniorityEnum = Field(
        description="Required seniority level for the position"
    )
    years_experience: YearsExperience = Field(
        description="Recommended years of experience range"
    )
