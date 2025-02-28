from typing import Literal

from langgraph.types import Command

from feeder.models.filters_query import FilterQuery, QueryIteration
from feeder.subgraph.linkedin_recruiter_subgraph.models.linkedin_recruiter_filters import (
    LinkedinRecruiterFilter,
    LocationFilter,
    TitleFilter,
    YearsOfExperienceFilter,
)
from src.feeder.state import OverallState
from src.feeder.utils.logger_setup import logger

SPECIFIC_TITLES_PERCENTAGE = 0.6


def create_linkedin_recruiter_queries(
    state: OverallState,
) -> Command[Literal["fake_node_1"]]:
    """Generate multiple LinkedIn Recruiter search queries."""
    try:
        logger.info("Generate linkedin recruiter queries")

        if not state.job_titles_classified:
            raise ValueError("Job titles must be classified first")

        if not state.json_object:
            raise ValueError("Job offer description must be provided")

        queries: list[LinkedinRecruiterFilter] = []

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
            else [None]
        )  # Use empty list as single "pair" if no keywords

        location_filters = [
            LocationFilter(title=location.name, id=location.id)
            for location in locations.items  # type: ignore
        ]

        yoe_range = seniority[-1].get_range()
        yoe_filters = YearsOfExperienceFilter(min=yoe_range[0], max=yoe_range[1])

        for keywords in keyword_pairs:
            logger.info(f"Generating queries for specific titles: {keywords}")

            title_filters = [
                TitleFilter(text=title, required=False) for title in specific_titles
            ]

            negative_title_filters = [
                TitleFilter(text=title, negative=True, required=False)
                for title in not_in_job_titles
            ]
            queries.append(
                LinkedinRecruiterFilter(
                    TITLES=title_filters + negative_title_filters,
                    KEYWORDS=" AND ".join(keywords) if keywords else None,
                    BING_GEO_SWR=location_filters,
                    TOTAL_YEARS_OF_EXPERIENCE_RANGE=yoe_filters,
                )
            )

        for title in reversed(broad_titles):
            logger.info(f"Generating queries for broad titles: {title}")
            for keywords in keyword_pairs:
                title_filters = [TitleFilter(text=title, required=False)]

                negative_title_filters = [
                    TitleFilter(text=title, negative=True, required=False)
                    for title in not_in_job_titles
                ]
                queries.append(
                    LinkedinRecruiterFilter(
                        TITLES=title_filters + negative_title_filters,
                        KEYWORDS=" AND ".join(keywords) if keywords else None,
                        BING_GEO_SWR=location_filters,
                        TOTAL_YEARS_OF_EXPERIENCE_RANGE=yoe_filters,
                    )
                )

        logger.info(f"Created {len(queries)} LinkedIn Recruiter queries")

        filter_queries = [
            FilterQuery(
                original_filters=query,
                iterations=[
                    QueryIteration(
                        filters=query,
                        count=None,
                        optimization_reason=None,
                        strategy_used=None,
                    )
                ],
            )
            for query in queries
        ]

        return Command(update={"query_results": filter_queries}, goto="fake_node_1")
    except Exception as e:
        logger.error(f"Error generating linkedin recruiter queries: {e}")
        raise e
