from typing import List

from langchain.pydantic_v1 import BaseModel, Field


class CareerPathAnalysis(BaseModel):

    logicalMove: bool = Field(
        ...,
        description="Boolean indicating whether this career move appears hierarchical logical based on the analysis.",
    )

    keyFactors: List[str] = Field(
        ...,
        description="List of main factors considered in determining the relevance score, such as hierarchy level comparison, typical industry progression, etc.",
    )

    explanation: str = Field(
        ...,
        description="A detailed explanation of the relevance score and overall analysis, including reasoning behind the logical_move determination."
        "Detail how the job posting aligns with or deviates from the expected career progression for this profile.",
    )

    careerImpact: str = Field(
        ...,
        description="An assessment of how this move might impact the candidate's long-term career prospects.",
    )
