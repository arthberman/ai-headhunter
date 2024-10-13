from typing import List

from pydantic import BaseModel, Field


class SchoolInfo(BaseModel):
    """Information about a school."""

    linkedin_url: str = Field(..., description="LinkedIn URL of the school")
    name: str = Field(..., description="The name of the school")
    description: str = Field(..., description="A brief description of the school")
    fields: List[str] = Field(
        ..., description="List of specialized fields related to the school"
    )
    ranking: str = Field(..., description="ranking/reputation of the school")
