import os
from typing import List, Literal

import requests
from dotenv import load_dotenv
from langchain_core.exceptions import LangChainException
from langgraph.types import Command

from feeder.models.people_search_filter import (
    CrustDataPeopleSearchResponse,
    PeopleSearchFilter,
)
from feeder.state import OverallState
from src.feeder.utils.logger_setup import logger

load_dotenv()


def get_search_count(
    state: OverallState,
) -> Command[Literal["optimization_subgraph"]]:
    """Get the search count of profiles scraped for a query."""
    try:
        if not state.query_results:
            raise ValueError("query_results is empty")

        logger.info("Getting search count for queries")
        queries_to_check: List[PeopleSearchFilter] = []

        # Get queries that have not been checked for total count
        for idx, query in enumerate(state.query_results):
            for iteration in query.iterations:
                if iteration.count is None:
                    queries_to_check.append(
                        PeopleSearchFilter(id=iteration.id, filters=iteration.filters)
                    )

        # If there are queries to be checked, use crust API to get counts for each query
        if queries_to_check:
            if not os.getenv("CRUSTDATA_API_KEY"):
                logger.error("CRUSTDATA_API_KEY not found in environment")
                raise ValueError("CRUSTDATA_API_KEY not found in environment")

            # Implement multiple iterations logic for each query
            for queries in queries_to_check:
                crust_api_people_search_filters = []
                for filters in queries.filters:
                    crust_api_people_search_filters.append(
                        {
                            "filter_type": filters.filter_type,
                            "type": filters.type,
                            "value": filters.value,
                        }
                    )

                res = requests.post(
                    "https://api.crustdata.com/screener/person/search",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": "Token " + os.getenv("CRUSTDATA_API_KEY", ""),
                    },
                    json={
                        "filters": crust_api_people_search_filters,
                        "preview": True,
                    },
                ).json()

                crust_data_people_search_response = CrustDataPeopleSearchResponse(**res)

                logger.info(
                    "Search count response: ", crust_data_people_search_response
                )

                # Update counts in state using query IDs
                for iteration in query.iterations:
                    if iteration.id == queries.id:
                        iteration.count = (
                            crust_data_people_search_response.total_display_count
                        )
                        break

        return Command(
            update={"query_results": state.query_results}, goto="optimization_subgraph"
        )
    except LangChainException as e:
        logger.error(f"Error getting search count: {e}")
        raise e
    except Exception as e:
        logger.error(f"Error getting search count: {e}")
        raise e
