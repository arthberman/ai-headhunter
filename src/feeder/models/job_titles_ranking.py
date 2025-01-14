from typing import List
from pydantic import BaseModel, Field
from feeder.models.job_titles import JobTitle


class JobTitlesRankings(BaseModel):
    """Pydantic model representing a list of job titles ranked from the most common one used on LinkedIn Sales Navigator to the least common one."""

    rankings: List[JobTitle] = Field(
        description="A list of job titles ranked from the most common one used on LinkedIn Sales Navigator to the least common one."
    )
