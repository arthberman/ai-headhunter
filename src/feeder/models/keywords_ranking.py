from typing import List, Optional
from pydantic import BaseModel, Field
from feeder.models.keywords import Keyword


class KeywordsRankings(BaseModel):
    """Pydantic model representing the classification of keywords into two categories: FAR and NEAR, based on their relevance and specificity to a job description."""

    far: Optional[List[str]] = Field(
        description="A list of keywords categorized as FAR, representing broad, general, or less directly connected terms.",
    )
    near: Optional[List[str]] = Field(
        description="A list of keywords categorized as NEAR, representing central, highly relevant, or specific terms.",
    )
