from pydantic import BaseModel, Field

from src.feeder.models.seniority_level import SeniorityEnum


class RawQuery(BaseModel):
    """Draft object used for preliminary LinkedIn Sales Navigator search queries.

    This object is designed to represent an initial search query structure, which will be evaluated later by judges.
    It serves as a preparatory step before constructing the finalized query object.
    """

    # number of elements: 10 elements
    in_job_titles: list[str] = Field(
        ...,
        alias="inJobTitles",
        description="List of job titles that are relevant to include in a LinkedIn Sales Navigator search to find perfect candidates given a job offer description",
    )
    not_in_job_titles: list[str] = Field(
        ...,
        alias="notInJobTitles",
        description="List of seniority indicators or precise job titles that must be excluded from a LinkedIn Sales Navigator search given a job offer description",
    )
    keywords: list[str] = Field(
        ...,
        description="List of keywords to find perfect candidates based on a given job offer description",
    )
    seniority: list[SeniorityEnum] = Field(
        ...,
        description="The seniority required for the job based on the job description and core responsibilities",
    )

    class Config:
        """Configuration class to avoid serialization problem."""

        populate_by_name = True
