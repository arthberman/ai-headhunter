from logging import getLogger
from typing import List, Optional, Sequence

from feeder.models.filters_query import OptimizationStrategy
from feeder.models.people_search_filter import (
    FilterOperationType,
    FilterType,
    TextFilter,
)
from src.feeder.subgraph.query_optimization.state import QueryOptimizationState

logger = getLogger(__name__)


def apply_strategy(
    filters: List[TextFilter],
    strategy: OptimizationStrategy,
    state: QueryOptimizationState,
) -> Optional[List[TextFilter]]:
    """Apply optimization strategy to filters."""
    logger.info("\n" + "-" * 50)
    logger.info(f"Applying strategy: {strategy.strategy_type}")
    logger.info("-" * 50)

    new_filters: Sequence[TextFilter] = filters.copy()

    if strategy.strategy_type == "remove_quotes":
        logger.info("Processing remove_quotes strategy")
        for filter in new_filters:
            if filter.filter_type == FilterType.CURRENT_TITLE:
                before = filter.value
                filter.value = [title.replace('\\"', '"') for title in filter.value]
                logger.info(f"Titles before: {before}")
                logger.info(f"Titles after: {filter.value}")

    elif strategy.strategy_type == "add_far_keywords":
        logger.info("Processing add_far_keywords strategy")
        if state.keywords_classified and state.keywords_classified.far:
            far_keywords = state.keywords_classified.far[:2]
            logger.info(f"Adding FAR keywords: {far_keywords}")
            new_filters.append(
                TextFilter(
                    filter_type=FilterType.KEYWORD,
                    type=FilterOperationType.IN,
                    value=far_keywords,
                )
            )

        else:
            logger.info("No FAR keywords found in state")

    elif strategy.strategy_type == "remove_keywords":
        logger.info("Processing remove_keywords strategy")
        new_filters = [f for f in new_filters if f.filter_type != FilterType.KEYWORD]

    elif strategy.strategy_type == "broaden_titles":
        logger.info("Processing broaden_titles strategy")
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
        logger.info("Processing remove_seniority strategy")
        new_filters = [
            f for f in new_filters if f.filter_type != FilterType.YEARS_OF_EXPERIENCE
        ]

    logger.info(f"Strategy {strategy.strategy_type} applied successfully")
    logger.info("-" * 50 + "\n")
    return new_filters
