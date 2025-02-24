from typing import Literal

from langgraph.types import Command

from feeder.models.filters_query import FilterQuery, QueryIteration
from feeder.models.people_search_filter import (
    FilterOperationType,
    FilterType,
    PeopleSearchFilter,
    TextFilter,
)
from feeder.state import OverallState
from src.feeder.utils.logger_setup import logger

# Percentage of titles to include in the first query
SPECIFIC_TITLES_PERCENTAGE = 0.6


def create_queries(state: OverallState) -> Command[Literal["fake_node_1"]]:
    """Generate multiple LinkedIn Sales Navigator search queries with a focus on precision and specificity.

    Strategy:
    1. First query: Include top 40% most precise job titles
    2. Subsequent queries: One query per job title, from most to least specific.
    """
    try:
        logger.info("Creating queries")
        if not state.job_titles_classified:
            raise ValueError("Job titles must be classified first")

        if not state.json_object:
            raise ValueError("Job offer description must be provided")

        queries = []

        job_titles = [job.title for job in state.job_titles_classified.rankings]

        near_keywords = []
        if state.keywords_classified:
            near_keywords = state.keywords_classified.near

        not_in_job_titles = []
        if state.json_object.not_in_job_titles:
            not_in_job_titles = state.json_object.not_in_job_titles

        locations = state.locations
        seniority = state.json_object.seniority

        # Split job titles - top 40% most specific for the first query
        split_index = int(
            len(job_titles) * SPECIFIC_TITLES_PERCENTAGE
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
            logger.info(f"Generating queries for specific titles: {keywords}")
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
                        value=[" AND ".join(keywords)],
                    )
                )

            # Add locations
            if locations:
                for location in locations.items:
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

            queries.append(PeopleSearchFilter(id=None, filters=filters))

        # Generate queries for broader titles
        for title in reversed(broad_titles):
            logger.info(f"Generating queries for broader titles: {title}")
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
                            value=[" AND ".join(keywords)],
                        )
                    )

                if locations:
                    for location in locations.items:
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

                queries.append(PeopleSearchFilter(id=None, filters=filters))

        # Instead of storing just the queries, create FilterQuery objects
        filter_queries = []
        for query in queries:
            filter_query = FilterQuery(
                original_filters=query.filters,
                iterations=[
                    QueryIteration(
                        count=None,
                        filters=query.filters,
                        optimization_reason=None,
                        strategy_used=None,
                    )
                ],
            )
            filter_queries.append(filter_query)
        logger.info(f"Created {len(filter_queries)} queries")

        return Command(update={"query_results": filter_queries}, goto="fake_node_1")
    except Exception as e:
        logger.error(f"Error creating queries: {e}")
        raise e
