from typing import List

from pydantic import BaseModel, Field


class OutputGraphState(BaseModel):
    """State of the enrichment graph."""

    context_initial: str = Field(
        ..., description="Raw job posting with all the context provided by the user"
    )
    context_enriched: List[str] = Field(..., description="List of context elements")
