from typing import List

from matcher.sub_graph.criterion_matcher.models import ScoredCriterion


def reducer_scored_criterion(
    existing: List[ScoredCriterion], new: List[ScoredCriterion]
) -> List[ScoredCriterion]:
    """Reducer that replaces existing criteria with new ones if IDs match."""
    # Create a dictionary of existing criteria, excluding ones that will be updated
    existing_dict = {
        criterion.id: criterion
        for criterion in existing
        if criterion.id not in {new_criterion.id for new_criterion in new}
    }

    # Add all new criteria
    for criterion in new:
        existing_dict[criterion.id] = criterion

    return list(existing_dict.values())
