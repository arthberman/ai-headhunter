from typing import Literal

from feeder.subgraph.query_optimization.state import QueryOptimizationState


def check_query_status(
    state: QueryOptimizationState,
) -> Literal["optimize_high_results", "optimize_low_results"]:
    """Determine next step in optimization workflow based on the current query."""
    if state.current_query_index is None:
        raise ValueError("current_query_index must be defined")

    current_query_index = state.current_query_index

    if not state.query_results:
        raise ValueError("query_results must be defined")

    current_query = state.query_results[current_query_index]

    if not current_query.iterations:
        raise ValueError(f"Query at index {current_query_index} has no iterations")

    latest_count = current_query.iterations[-1].count
    if latest_count is None:
        raise ValueError(
            f"Latest iteration for query {current_query_index} has no count"
        )

    # route based on result count
    if latest_count > 1000:
        return "optimize_high_results"
    elif latest_count < 30:
        return "optimize_low_results"
    else:
        raise ValueError(f"Unexpected count value: {latest_count}")
