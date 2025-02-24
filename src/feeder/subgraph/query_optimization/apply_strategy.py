from logging import getLogger
from typing import List, Union, cast

from feeder.models.filters_query import OptimizationStrategy
from feeder.models.people_search_filter import (
    FilterOperationType,
    FilterType,
    TextFilter,
)
from feeder.subgraph.linkedin_recruiter_subgraph.models.linkedin_recruiter_filters import (
    LinkedinRecruiterFilter,
    TitleFilter,
)
from src.feeder.subgraph.query_optimization.state import QueryOptimizationState

logger = getLogger(__name__)


def apply_strategy(
    filters: List[TextFilter] | LinkedinRecruiterFilter,
    strategy: OptimizationStrategy,
    state: QueryOptimizationState,
) -> Union[List[TextFilter], LinkedinRecruiterFilter]:
    """Apply optimization strategy to filters.

    Returns the new filters if the strategy was applied successfully, otherwise returns None.
    """
    logger.info("\n" + "-" * 50)
    logger.info(f"Applying strategy: {strategy.strategy_type}")
    logger.info("-" * 50)

    new_filters = filters.copy()

    if isinstance(new_filters, LinkedinRecruiterFilter):
        # Add FAR keywords to the query if available
        if strategy.strategy_type == "add_far_keywords":
            logger.info("Performing add_far_keywords strategy")

            if state.keywords_classified and state.keywords_classified.far:
                far_keywords = state.keywords_classified.far[:2]
                logger.info(f"Adding FAR keywords: {far_keywords}")

                new_filters.KEYWORDS = [new_filters.KEYWORDS] + far_keywords

                return new_filters
            else:
                logger.info("No FAR keywords found in state")
                return new_filters
        elif strategy.strategy_type == "remove_keywords":
            logger.info("Performing remove_keywords strategy")
            new_filters.KEYWORDS = []

            return new_filters
        elif strategy.strategy_type == "broaden_titles":
            logger.info("Performing broaden_titles strategy")

            if new_filters.TITLES:
                new_titles = [
                    title.text.replace("Senior ", "").replace("Lead ", "")
                    for title in new_filters.TITLES
                ]
                new_filters.TITLES = [
                    TitleFilter(text=title, required=False) for title in new_titles
                ]

            return new_filters
        else:
            logger.warning(f"Unknown strategy: {strategy.strategy_type}")
            return new_filters
    else:
        new_filters = cast(List[TextFilter], new_filters)

        # Removes quotes from titles
        if strategy.strategy_type == "remove_quotes":
            logger.info("Performing remove_quotes strategy")
            for filter in new_filters:
                if filter.filter_type == FilterType.CURRENT_TITLE:
                    filter.value = [title.replace('\\"', '"') for title in filter.value]

            return new_filters

        elif strategy.strategy_type == "add_far_keywords":
            logger.info("Performing add_far_keywords strategy")

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

            return new_filters

        # Removes keywords from the query
        elif strategy.strategy_type == "remove_keywords":
            logger.info("Performing remove_keywords strategy")
            new_filters = [
                f for f in new_filters if f.filter_type != FilterType.KEYWORD
            ]

            return new_filters

        # Broadens titles by removing quotes and specific qualifiers
        elif strategy.strategy_type == "broaden_titles":
            logger.info("Performing broaden_titles strategy")
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

            return new_filters

        # Removes seniority from the query
        elif strategy.strategy_type == "remove_seniority":
            logger.info("Performing remove_seniority strategy")
            new_filters = [
                f
                for f in new_filters
                if f.filter_type != FilterType.YEARS_OF_EXPERIENCE
            ]

            return new_filters
        else:
            logger.error(f"Unknown strategy: {strategy.strategy_type}")
            raise ValueError(f"Unknown strategy: {strategy.strategy_type}")
