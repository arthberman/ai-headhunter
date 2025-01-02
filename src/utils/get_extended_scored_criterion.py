from typing import List, Optional, Union

from pydantic import Field

from matcher.sub_graph.criterion_matcher.models import ScoredCriterion
from setup.models.scorecard import Category, Priority, Scorecard


class ExtendedScoredCriterion(ScoredCriterion):
    """Extended scored criterion."""

    description: str = Field(description="Description of the criterion")
    priority: Priority = Field(description="Priority of the criterion")
    category: Category = Field(description="Category of the criterion")


def get_extended_scored_criterion(
    scored_criterion: ScoredCriterion,
    scorecard: Scorecard,
    priority: Optional[Union[Priority, List[Priority]]] = None,
    category: Optional[Union[Category, List[Category]]] = None,
):
    """Get the extended scored criterion with the scorecard.

    Args:
        scored_criterion: The scored criterion to extend
        scorecard: The scorecard containing the criteria
        priority: Optional filter for priority(s). Can be a single Priority or a list
        category: Optional filter for category(s). Can be a single Category or a list

    Returns:
        List of extended scored criteria matching the filters
    """
    # Convert single values to lists for consistent handling
    priority_levels = (
        [priority]
        if isinstance(priority, Priority)
        else priority
        if isinstance(priority, list)
        else None
    )

    categories = (
        [category]
        if isinstance(category, Category)
        else category
        if isinstance(category, list)
        else None
    )

    extended_scored_criterion: List[ExtendedScoredCriterion] = []
    for scored_criterion in scored_criterion:
        criterion = next(
            (c for c in scorecard.criteria if c.id == scored_criterion.id),
            None,
        )
        if criterion:
            # Skip if priority filter is set and doesn't match
            if priority_levels and criterion.priority not in priority_levels:
                continue

            # Skip if category filter is set and doesn't match
            if categories and criterion.category not in categories:
                continue

            extended_scored_criterion.append(
                ExtendedScoredCriterion(
                    **scored_criterion.model_dump(),
                    description=criterion.description,
                    priority=criterion.priority.value,
                    category=criterion.category.value,
                )
            )

    return extended_scored_criterion
