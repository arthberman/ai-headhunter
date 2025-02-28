from typing import Literal, Optional

from langgraph.types import Command

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
from feeder.subgraph.query_optimization.apply_strategy import apply_strategy
from src.feeder.subgraph.query_optimization.state import QueryOptimizationState
from src.feeder.utils.logger_setup import logger


def optimize_high_results(
    state: QueryOptimizationState,
) -> Command[Literal["analyze_current_query"]]:
    """Optimize queries with too many results.

    Optimize queries that return too many results using two strategies:

    1. If FAR keywords are present:
       - Adds FAR keywords to narrow down result

    2. If multiple job titles exist:
       - Splits the query into separate queries, one per job title
       - Other filters remain unchanged for each split query
    """
    try:
        current_query_index = state.current_query_index

        current_query = state.query_results[current_query_index]
        logger.info(
            "\n"
            + "=" * 50
            + "Checking high results optimization conditions:"
            + "=" * 50
        )

        # Check for FAR keywords
        has_far_keywords = state.keywords_classified and state.keywords_classified.far
        logger.info(f"- Has FAR keywords: {has_far_keywords}")

        # Try adding FAR keywords first
        if has_far_keywords:
            logger.info("Attempting to add FAR keywords to reduce results")

            next_strategy = OptimizationStrategy(strategy_type="add_far_keywords")
            optimized_filters = apply_strategy(
                current_query.latest_filters, next_strategy, state
            )

            next_strategy.attempted = True
            current_query.optimization_attempt += 1
            current_query.add_iteration(
                filters=optimized_filters,
                optimization_reason="Added FAR keywords to reduce results",
                strategy_used="add_far_keywords",
            )

            return Command(
                update={"query_results": state.query_results},
                goto="analyze_current_query",
            )
        else:
            # If no FAR keywords, check job titles

            if isinstance(current_query.latest_filters, LinkedinRecruiterFilter):
                current_filters = current_query.latest_filters.model_copy()
                job_titles: Optional[list[TitleFilter]] = []

                if current_filters.TITLES:
                    for title in current_filters.TITLES:
                        if title.negative is False:
                            job_titles.append(title)

                if not job_titles or len(job_titles) <= 1:
                    logger.info("Query has single job title - moving to next query")

                    current_query.is_optimized = True
                    return Command(
                        update={
                            "query_results": state.query_results,
                            "current_query_index": current_query_index + 1,
                        },
                        goto="analyze_current_query",
                    )
                else:
                    new_queries = []

            else:
                current_filters = current_query.latest_filters.copy()
                job_titles_filter: Optional[TextFilter] = None

                # Get the in_job_title filters
                for filter in current_filters:
                    if (
                        filter.filter_type == FilterType.CURRENT_TITLE
                        and filter.type == FilterOperationType.IN
                    ):
                        job_titles_filter = filter
                        break

                # If single job title, move to next query
                if not job_titles_filter or len(job_titles_filter.value) <= 1:
                    logger.info("Query has single job title - moving to next query")

                    current_query.is_optimized = True
                    return Command(
                        update={
                            "query_results": state.query_results,
                            "current_query_index": current_query_index + 1,
                        },
                        goto="analyze_current_query",
                    )
                else:
                    # Multiple job titles - split each job title to a separate query
                    other_filters = [
                        f for f in current_filters if f != job_titles_filter
                    ]
                    new_filters_list = []

                    for job_title in job_titles_filter.value:
                        new_filters = other_filters.copy()
                        new_filters.append(
                            TextFilter(
                                filter_type=FilterType.CURRENT_TITLE,
                                type=FilterOperationType.IN,
                                value=[job_title],
                            )
                        )
                        new_filters_list.append(new_filters)

                    # Create new queries and add them to main results list
                    new_queries = current_query.split_query(
                        new_filters_list, "Split query by individual job titles"
                    )

            state.query_results.extend(new_queries)
            current_query.is_optimized = True

            return Command(
                update={
                    "query_results": state.query_results,
                    "current_query_index": current_query_index + 1,
                },
                goto="analyze_current_query",
            )
    except Exception as e:
        logger.error(f"Error optimizing high results: {e}")
        raise e
