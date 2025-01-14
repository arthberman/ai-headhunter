from langgraph.graph import END

from feeder.subgraph.query_optimization.state import QueryOptimizationState


def check_query_status(state: QueryOptimizationState):
    """Determine next step in optimization workflow based on the current query."""
    current_query_index = state.current_query_index
    current_query = state.query_results.results[current_query_index]

    latest_count = current_query.iterations[-1].count
    # route based on result count
    if latest_count > 1000:
        return "optimize_high_results"
    elif latest_count < 30:
        return "optimize_low_results"
