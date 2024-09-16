from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel
from scorecard.models.scorecard import (
    CriteriaType,
    ImportanceLevel,
    Scorecard,
    BaseCriterion,
    ScoringDistribution,
)


class ActionType(str, Enum):
    DELETE = "DELETE"
    ADD = "ADD"
    MOVE_TO_NICE_TO_HAVE = "MOVE_TO_NICE_TO_HAVE"


class StructureAction(BaseModel):
    actionType: ActionType
    importance: ImportanceLevel
    type: CriteriaType
    description: str
    scoring_distribution: ScoringDistribution
    distribution_params: Optional[Dict[str, float]]


class StructureJudgeOutput(BaseModel):
    is_structure_valid: bool
    structure_actions: Optional[List[StructureAction]]


# New class to represent a criterion with its importance level
class CriterionWithImportance(BaseCriterion):
    importance: ImportanceLevel


# Helper function to convert Scorecard to a list of CriterionWithImportance
def scorecard_to_criteria_list(scorecard: Scorecard) -> List[CriterionWithImportance]:
    criteria_list = []
    for importance, criteria in [
        (ImportanceLevel.MUST_HAVE, scorecard.mustHaveCriteria),
        (ImportanceLevel.IMPORTANT, scorecard.importantCriteria),
        (ImportanceLevel.NICE_TO_HAVE, scorecard.niceToHaveCriteria),
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
        mustHaveCriteria=must_have,
        importantCriteria=important,
        niceToHaveCriteria=nice_to_have,
    )
