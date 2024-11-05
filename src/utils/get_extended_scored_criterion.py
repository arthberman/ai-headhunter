from typing import List, Optional, Union

from pydantic import Field

from analysis.sub_graph.criterion_analysis.models import ScoredCriterion
from scorecard.models.scorecard import CriterionType, ImportanceLevel, Scorecard


class ExtendedScoredCriterion(ScoredCriterion):
    """Extended scored criterion."""

    description: str = Field(description="Description of the criterion")
    importance_level: ImportanceLevel = Field(
        description="Importance level of the criterion"
    )
    criterion_type: CriterionType = Field(description="Type of the criterion")


def get_extended_scored_criterion(
    scored_criterion: ScoredCriterion,
    scorecard: Scorecard,
    importance_level: Optional[Union[ImportanceLevel, List[ImportanceLevel]]] = None,
    criterion_type: Optional[Union[CriterionType, List[CriterionType]]] = None,
):
    """Get the extended scored criterion with the scorecard.

    Args:
        scored_criterion: The scored criterion to extend
        scorecard: The scorecard containing the criteria
        importance_level: Optional filter for importance level(s). Can be a single ImportanceLevel or a list
        criterion_type: Optional filter for criterion type(s). Can be a single CriterionType or a list

    Returns:
        List of extended scored criteria matching the filters
    """
    # Convert single values to lists for consistent handling
    importance_levels = (
        [importance_level]
        if isinstance(importance_level, ImportanceLevel)
        else importance_level
        if isinstance(importance_level, list)
        else None
    )

    criterion_types = (
        [criterion_type]
        if isinstance(criterion_type, CriterionType)
        else criterion_type
        if isinstance(criterion_type, list)
        else None
    )

    extended_scored_criterion: List[ExtendedScoredCriterion] = []
    for scored_criterion in scored_criterion:
        criterion = next(
            (c for c in scorecard.criteria if c.id == scored_criterion.id),
            None,
        )
        if criterion:
            # Skip if importance_level filter is set and doesn't match
            if (
                importance_levels
                and criterion.importance_level not in importance_levels
            ):
                continue

            # Skip if criterion_type filter is set and doesn't match
            if criterion_types and criterion.type not in criterion_types:
                continue

            extended_scored_criterion.append(
                ExtendedScoredCriterion(
                    **scored_criterion.model_dump(),
                    description=criterion.description,
                    importance_level=criterion.importance_level.value,
                    criterion_type=criterion.type.value,
                )
            )

    return extended_scored_criterion
