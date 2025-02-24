from typing import List

from pydantic import BaseModel, Field


class JobTitleList(BaseModel):
    """Model for the in job titles."""

    titles: List[str] = Field(
        description="List of job titles that are relevant to the job offer description.",
        alias="inJobTitles",
    )
