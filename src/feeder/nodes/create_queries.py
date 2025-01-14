from typing import List

from feeder.models.filters_query import FilterQuery, FilterQueryList, QueryIteration
from feeder.models.people_search_filter import (
    FilterOperationType,
    FilterType,
    PeopleSearchFilter,
    TextFilter,
)
from feeder.state import OverallState
from feeder.subgraph.query_optimization.state import QueryOptimizationState


def create_queries(state: OverallState) -> QueryOptimizationState:
    """Generate multiple LinkedIn Sales Navigator search queries with a focus on precision and specificity.

    Strategy:
    1. First query: Include top 40% most precise job titles
    2. Subsequent queries: One query per job title, from most to least specific.
    """
    if not state.job_titles_classified:
        raise ValueError("Job titles must be classified first")

    queries = []
    job_titles = [job.title for job in state.job_titles_classified.rankings]
    near_keywords = (
        state.keywords_classified.get("near", []) if state.keywords_classified else []
    )
    not_in_job_titles = state.json_object.exclude
    locations = state.locations.locations
    seniority = state.json_object.seniority

    # Split job titles - top 40% most specific for the first query
    num_titles = len(job_titles)
    split_index = int(
        num_titles * 0.6
    )  # index for 40% split (from the end since most precise are at the end)
    specific_titles = job_titles[split_index:]  # top 40% most precise titles
    broad_titles = job_titles[:split_index]  # remaining 60% titles

    # If we have keywords, split them into pairs, otherwise use empty list
    keyword_pairs = (
        [near_keywords[i : i + 2] for i in range(0, len(near_keywords), 2)]
        if near_keywords
        else [[]]
    )  # Use empty list as single "pair" if no keywords

    # Generate queries for specific titles with each keyword pair
    for keywords in keyword_pairs:
        filters = []

        # Add job titles filter
        filters.append(
            TextFilter(
                filter_type=FilterType.CURRENT_TITLE,
                type=FilterOperationType.IN,
                value=specific_titles,
            )
        )

        # Add NOT IN job titles
        if not_in_job_titles:
            filters.append(
                TextFilter(
                    filter_type=FilterType.CURRENT_TITLE,
                    type=FilterOperationType.NOT_IN,
                    value=not_in_job_titles,
                )
            )

        # Add keywords only if we have them
        if keywords:
            filters.append(
                TextFilter(
                    filter_type=FilterType.KEYWORD,
                    type=FilterOperationType.IN,
                    value=keywords,
                )
            )

        # Add locations
        for location in locations:
            filters.append(
                TextFilter(
                    filter_type=FilterType.REGION,
                    type=FilterOperationType.IN,
                    value=[location.name],
                )
            )

        # Add seniority
        if seniority:
            for seniority_level in seniority:
                filters.append(
                    TextFilter(
                        filter_type=FilterType.YEARS_OF_EXPERIENCE,
                        type=FilterOperationType.IN,
                        value=[seniority_level.value],
                    )
                )

        queries.append(PeopleSearchFilter(filters=filters))

    # Generate queries for broader titles
    for title in reversed(broad_titles):
        for keywords in keyword_pairs:
            filters = []

            # Add single broad job title
            filters.append(
                TextFilter(
                    filter_type=FilterType.CURRENT_TITLE,
                    type=FilterOperationType.IN,
                    value=[title],
                )
            )

            # Add rest of filters (same as above)
            if not_in_job_titles:
                filters.append(
                    TextFilter(
                        filter_type=FilterType.CURRENT_TITLE,
                        type=FilterOperationType.NOT_IN,
                        value=not_in_job_titles,
                    )
                )

            # Add keywords only if we have them
            if keywords:
                filters.append(
                    TextFilter(
                        filter_type=FilterType.KEYWORD,
                        type=FilterOperationType.IN,
                        value=keywords,
                    )
                )

            for location in locations:
                filters.append(
                    TextFilter(
                        filter_type=FilterType.REGION,
                        type=FilterOperationType.IN,
                        value=[location.name],
                    )
                )

            if seniority:
                for seniority_level in seniority:
                    filters.append(
                        TextFilter(
                            filter_type=FilterType.YEARS_OF_EXPERIENCE,
                            type=FilterOperationType.IN,
                            value=[seniority_level.value],
                        )
                    )

            queries.append(PeopleSearchFilter(filters=filters))

    # Instead of storing just the queries, create FilterQuery objects
    filter_queries = []
    for query in queries:
        filter_query = FilterQuery(
            original_filters=query,  # Pass PeopleSearchFilter directly
            iterations=[
                QueryIteration(
                    filters=query,  # Pass PeopleSearchFilter directly
                    count=None,
                )
            ],
        )
        filter_queries.append(filter_query)

    # Store as FilterQueryList
    # state.query_results = FilterQueryList(
    #     results=filter_queries
    # )  # Note: changed from queries to results
    out = FilterQueryList(results=filter_queries)
    # return state
    print(out)
    print(state.query_results)
    return {"query_results": out}
