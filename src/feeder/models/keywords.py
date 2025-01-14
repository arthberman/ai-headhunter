from typing import List

from pydantic import BaseModel, Field


class Keyword(BaseModel):
    label: str = Field(
        description="A term extracted from the job offer description and which is specific to the job"
    )


class Keywords(BaseModel):
    keywords: List[Keyword]
