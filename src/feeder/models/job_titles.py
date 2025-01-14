from typing import List

from pydantic import BaseModel, Field


class JobTitle(BaseModel):
    """A job title that fits with the given job offer description."""

    title: str = Field(
        description="A job title that fits with the given job offer description"
    )