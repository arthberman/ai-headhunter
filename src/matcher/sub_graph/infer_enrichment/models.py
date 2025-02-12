from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from matcher.models.language import LanguageProficiency


class InferredAttributeType(Enum):
    """Inferred attributes."""

    LANGUAGES = "languages"
    INDUSTRY_SECTOR = "industry_sector"
    CULTURE = "culture"
    ROLE_TRAJECTORY = "role_trajectory"


class InferredAttribute(BaseModel):
    """Inferred attribute."""

    type: InferredAttributeType = Field(
        ..., description="Type of the inferred attribute"
    )
    description: str = Field(..., description="The inferred attribute description")
    languages: Optional[List[LanguageProficiency]] = Field(
        default=None, description="The inferred languages"
    )

    def model_post_init(self, __context) -> None:
        """Validate that languages are only present for LANGUAGES type."""
        if self.type != InferredAttributeType.LANGUAGES and self.languages is not None:
            raise ValueError("languages field can only be set when type is LANGUAGES")
        if self.type == InferredAttributeType.LANGUAGES and self.languages is None:
            raise ValueError("languages field must be set when type is LANGUAGES")


def reducer_inferred_attributes(
    existing: List[InferredAttribute], new: List[InferredAttribute]
) -> List[InferredAttribute]:
    """Reducer that merges inferred attributes, replacing existing ones of the same type."""
    existing_dict = {
        attribute.type: attribute
        for attribute in existing
        if attribute.type not in {new_attribute.type for new_attribute in new}
    }

    for attribute in new:
        existing_dict[attribute.type] = attribute

    return list(existing_dict.values())
