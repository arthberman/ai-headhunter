from typing import List, Optional
from pydantic import BaseModel, Field


class KeywordsRankings(BaseModel):
    """Pydantic model representing the classification of keywords into two categories: FAR and NEAR."""

    far: List[str] = Field(
        default_factory=list,
        description="A list of keywords categorized as FAR, representing broad, general, or less directly connected terms.",
    )
    near: List[str] = Field(
        default_factory=list,
        description="A list of keywords categorized as NEAR, representing central, highly relevant, or specific terms.",
    )

    model_config = {"from_attributes": True, "populate_by_name": True}
