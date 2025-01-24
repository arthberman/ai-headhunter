import uuid
from logging import getLogger
from typing import List

from langgraph.types import interrupt
from pydantic import BaseModel

from feeder.models.people_search_filter import PeopleSearchFilter
from feeder.state import OverallState

logger = getLogger(__name__)


class SearchCountResponse(BaseModel):
    """Expected response structure from search count interrupt."""

    counts: List[tuple[uuid.UUID, int]]  # List of (query_id, count) tuples


def node_get_search_count(state: OverallState) -> OverallState:
    """Get the search count for a query."""
    if not state.query_results:
        return state

    queries_to_check: List[PeopleSearchFilter] = []
    query_indices: List[int] = []

    # Find all queries that need count checking
    for idx, query in enumerate(state.query_results):
        for iteration in query.iterations:
            if iteration.count is None:
                queries_to_check.append(
                    {"query": {"filters": iteration.filters}, "id": iteration.id}
                )
                query_indices.append(idx)

    # If we have queries to check, interrupt and get counts
    if queries_to_check:
        res = SearchCountResponse.model_validate(
            interrupt(
                {
                    "action": "get_search_count",
                    "queries": queries_to_check,
                }
            )
        )

        # Update counts in state using query IDs
        for query_id, count in res.counts:
            for query in state.query_results:
                for iteration in query.iterations:
                    if iteration.id == query_id:
                        iteration.count = count
                        break

    return state
