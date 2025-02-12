from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Outcome(Enum):
    """Outcome of the assessment."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REVIEW = "review"


class DecisionType(Enum):
    """Decision types."""

    ALL_REQUIRED_CRITERIA = "all_required_criteria"
    LOCATION = "location"
    HIERARCHY_MOVE = "hierarchy_move"
    OPENESS_TO_WORK = "openess_to_work"
    INTENT_TO_MOVE = "intent_to_move"
    REDFLAG_STABILITY = "redflag_stability"


class Decision(BaseModel):
    """Decision."""

    type: DecisionType = Field(..., description="Type of the decision")
    outcome: Outcome = Field(..., description="Outcome of the decision")
    explanation: str = Field(..., description="Explanation of the decision")


class Conclusion(BaseModel):
    """Overall conclusion of the matcher."""

    outcome: Outcome = Field(..., description="Outcome of the matcher")
    explanation: str = Field(
        ...,
        description="Explanation of the outcome in one-line paragraph (max 600 characters)",
    )
    summary: List[str] = Field(
        ...,
        description="""Summary of the conclusion as a list of bullet points.
        Use an emoji at the beginning of each element. Focus on the elements
        that were structural in your decisions. Max 70 characters per item""",
    )


def reducer_decisions(existing: List[Decision], new: List[Decision]) -> List[Decision]:
    """Reducer that merges decisions, replacing existing ones of the same type."""
    existing_dict = {
        element.type: element
        for element in existing
        if element.type not in {new_element.type for new_element in new}
    }

    for element in new:
        existing_dict[element.type] = element

    return list(existing_dict.values())
