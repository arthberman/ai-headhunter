from typing import List

from langgraph.types import interrupt
from pydantic import BaseModel

from feeder.state import OverallState


class SearchCountResponse(BaseModel):
    """Expected response structure from search count interrupt."""

    counts: List[int]


def node_get_search_count(state: OverallState) -> OverallState:
    """Get the search count for a query."""
    # Skip if no query results
    if not state.query_results:
        return state

    queries_to_check = []

    # Find queries that need count checking
    for query in state.query_results.results:
        if query.iterations and query.iterations[-1].count is None:
            current_query = query.latest_filters
            queries_to_check.append(current_query)

    # If we have queries to check, interrupt and get counts
    if queries_to_check:
        res = SearchCountResponse.model_validate(
            interrupt(
                {
                    "task": "get_search_count",
                    "queries": queries_to_check,
                }
            )
        )

        # Update counts in state
        count_index = 0
        for query in state.query_results.results:
            if query.iterations and query.iterations[-1].count is None:
                query.iterations[-1].count = res.counts[count_index]
                count_index += 1

    return state
