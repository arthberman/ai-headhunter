from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from models.scorecard.scorecard import (
    BaseCriterion,
    CriterionType,
    ImportanceLevel,
    Scorecard,
)


class ActionType(str, Enum):
    """The type of action to perform on the scorecard."""

    DELETE = "DELETE"
    ADD = "ADD"
    MOVE_TO_NICE_TO_HAVE = "MOVE_TO_NICE_TO_HAVE"


class StructureAction(BaseModel):
    """An action to perform on the scorecard."""

    actionType: ActionType
    importance: ImportanceLevel
    type: CriterionType
    description: str


class StructureJudgeOutput(BaseModel):
    """The output of the structure judge."""

    is_structure_valid: bool
    next_actions: Optional[List[StructureAction]]


# New class to represent a criterion with its importance level
class CriterionWithImportance(BaseCriterion):
    """A criterion with its importance level."""

    importance: ImportanceLevel


# Helper function to convert Scorecard to a list of CriterionWithImportance
def scorecard_to_criteria_list(scorecard: Scorecard) -> List[CriterionWithImportance]:
    """Convert a scorecard to a list of criteria with their importance level."""
    criteria_list = []
    for importance, criteria in [
        (ImportanceLevel.MUST_HAVE, scorecard.must_have_criteria),
        (ImportanceLevel.IMPORTANT, scorecard.important_criteria),
        (ImportanceLevel.NICE_TO_HAVE, scorecard.nice_to_have_criteria),
    ]:
        for criterion in criteria:
            criteria_list.append(
                CriterionWithImportance(**criterion.dict(), importance=importance)
            )
    return criteria_list


# Helper function to convert a list of CriterionWithImportance back to a Scorecard
def criteria_list_to_scorecard(
    criteria_list: List[CriterionWithImportance],
) -> Scorecard:
    """Convert a list of criteria with their importance level back to a scorecard."""
    must_have = []
    important = []
    nice_to_have = []
    for criterion in criteria_list:
        criterion_dict = criterion.dict(exclude={"importance"})
        if criterion.importance == ImportanceLevel.MUST_HAVE:
            must_have.append(BaseCriterion(**criterion_dict))
        elif criterion.importance == ImportanceLevel.IMPORTANT:
            important.append(BaseCriterion(**criterion_dict))
        elif criterion.importance == ImportanceLevel.NICE_TO_HAVE:
            nice_to_have.append(BaseCriterion(**criterion_dict))
    return Scorecard(
        must_have_criteria=must_have,
        important_criteria=important,
        nice_to_have_criteria=nice_to_have,
    )
