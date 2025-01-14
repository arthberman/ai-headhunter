from typing import List

from pydantic import BaseModel, Field


class FeedbackResponse(BaseModel):
    """Represents the categorized keyword feedback containing precise and broad keyword lists."""

    precise_keywords: List[str] = Field(
        description="List of keywords that are specific and likely to yield targeted search results",
        default_factory=list,
    )
    broad_keywords: List[str] = Field(
        description="List of keywords that are general and likely to return a larger pool of results",
        default_factory=list,
    )