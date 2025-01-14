from langgraph.types import Command
from typing_extensions import Literal

from feeder.models.filters_query import OptimizationStrategy
from feeder.models.people_search_filter import (
    FilterOperationType,
    FilterType,
    PeopleSearchFilter,
    TextFilter,
)
from feeder.subgraph.query_optimization.nodes.apply_strategy import apply_strategy
from feeder.subgraph.query_optimization.state import QueryOptimizationState


def optimize_high_results(state: QueryOptimizationState):
    """Optimize queries with too many results."""
    current_query = state.query_results.results[state.current_query_index]
    current_query_index = state.current_query_index

    print("\n" + "=" * 50)
    print("Checking high results optimization conditions:")
    print(
        f"- Current result count: {current_query.iterations[current_query.optimization_attempt].count}"
    )

    # Check for FAR keywords
    has_far_keywords = (
        state.keywords_classified
        and state.keywords_classified.get("far")
        and len(state.keywords_classified["far"]) > 0
    )
    print(f"- Has FAR keywords: {has_far_keywords}")

    if current_query.iterations[current_query.optimization_attempt].count > 1000:
        if has_far_keywords:
            # Try adding FAR keywords first
            print("Attempting to add FAR keywords to reduce results")
            next_strategy = OptimizationStrategy(strategy_type="add_far_keywords")
            optimized_filters = apply_strategy(
                current_query.latest_filters, next_strategy, state
            )

            if optimized_filters:
                next_strategy.attempted = True
                current_query.optimization_attempt += 1
                current_query.add_iteration(
                    filters=optimized_filters,
                    profile_count=0,
                    optimization_reason="Added FAR keywords to reduce results",
                    strategy_used="add_far_keywords",
                )
                return Command(
                    graph=Command.PARENT,
                    update={"query_results": state.query_results},
                    goto="get_search_count",
                )

        # If no FAR keywords, check job titles
        current_filters = current_query.latest_filters.filters.copy()
        job_titles_filter = None
        for filter in current_filters:
            if (
                filter.filter_type == FilterType.CURRENT_TITLE
                and filter.type == FilterOperationType.IN
            ):
                job_titles_filter = filter
                break

        # If single job title, move to next query
        if not job_titles_filter or len(job_titles_filter.value) <= 1:
            print("Query has single job title - moving to next query")
            current_query.is_optimized = True
            current_query_index += 1
            return Command(
                graph=Command.PARENT,
                update={
                    "query_results": state.query_results,
                    "current_query_index": current_query_index,
                },
                goto="get_search_count",
            )

        # Multiple job titles - split the query
        other_filters = [f for f in current_filters if f != job_titles_filter]
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
            new_filters_list.append(PeopleSearchFilter(filters=new_filters))

        current_query.split_query(
            new_filters_list, "Split query by individual job titles"
        )
        print("Query split into multiple queries by job titles")

    return Command(
        graph=Command.PARENT,
        update={"query_results": state.query_results},
        goto="get_search_count",
    )
