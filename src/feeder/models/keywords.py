from typing import List

from pydantic import BaseModel, Field


class Keyword(BaseModel):
    """Represents a keyword extracted from a job description."""

    label: str = Field(
        description="A term extracted from the job offer description and which is specific to the job"
    )


class Keywords(BaseModel):
    """Represents a list of keywords extracted from a job description."""

    keywords: List[Keyword]
