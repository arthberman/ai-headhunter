from typing import Optional

from feeder.models.filters_query import OptimizationStrategy
from feeder.models.people_search_filter import (
    FilterOperationType,
    FilterType,
    PeopleSearchFilter,
    TextFilter,
)
from feeder.subgraph.query_optimization.state import QueryOptimizationState


def apply_strategy(
    filters: PeopleSearchFilter,
    strategy: OptimizationStrategy,
    state: QueryOptimizationState,
) -> Optional[PeopleSearchFilter]:
    """Apply optimization strategy to filters."""
    print("\n" + "-" * 50)
    print(f"Applying strategy: {strategy.strategy_type}")
    print("-" * 50)

    new_filters = filters.filters.copy()

    if strategy.strategy_type == "remove_quotes":
        print("Processing remove_quotes strategy")
        for filter in new_filters:
            if filter.filter_type == FilterType.CURRENT_TITLE:
                before = filter.value
                filter.value = [title.replace('\\"', '"') for title in filter.value]
                print(f"Titles before: {before}")
                print(f"Titles after: {filter.value}")

    elif strategy.strategy_type == "add_far_keywords":
        print("Processing add_far_keywords strategy")
        if state.keywords_classified and state.keywords_classified.get("far"):
            far_keywords = state.keywords_classified.get("far", [])[:2]
            print(f"Adding FAR keywords: {far_keywords}")
            new_filters.append(
                TextFilter(
                    filter_type=FilterType.KEYWORD,
                    type=FilterOperationType.IN,
                    value=far_keywords,
                )
            )
        else:
            print("No FAR keywords found in state")

    elif strategy.strategy_type == "remove_keywords":
        print("Processing remove_keywords strategy")
        new_filters = [f for f in new_filters if f.filter_type != FilterType.KEYWORD]

    elif strategy.strategy_type == "broaden_titles":
        print("Processing broaden_titles strategy")
        title_filters = [
            f for f in new_filters if f.filter_type == FilterType.CURRENT_TITLE
        ]
        if title_filters:
            # Remove quotes and specific qualifiers
            broader_titles = [
                title.replace('"', "").replace("Senior ", "").replace("Lead ", "")
                for title in title_filters[0].value
            ]
            title_filters[0].value = broader_titles

    elif strategy.strategy_type == "remove_seniority":
        print("Processing remove_seniority strategy")
        new_filters = [
            f for f in new_filters if f.filter_type != FilterType.YEARS_OF_EXPERIENCE
        ]

    print(f"Strategy {strategy.strategy_type} applied successfully")
    print("-" * 50 + "\n")
    return PeopleSearchFilter(filters=new_filters)
