from typing import List

from pydantic import BaseModel, Field


class JobTitle(BaseModel):
    """A job title that fits with the given job offer description."""

    title: str = Field(
        description="A job title that fits with the given job offer description"
    )


class JobTitlesRankings(BaseModel):
    """Pydantic model representing a list of job titles ranked from the most common one used on LinkedIn Sales Navigator to the least common one."""

    rankings: List[JobTitle] = Field(
        description="A list of job titles ranked from the most common one used on LinkedIn Sales Navigator to the least common one."
    )
