from typing import List

from langchain.pydantic_v1 import BaseModel, Field


class KnowledgePoint(BaseModel):
    description: str = Field(description="The description of the knowledge point")
    type: str = Field(description="Type of this knowledge point")
