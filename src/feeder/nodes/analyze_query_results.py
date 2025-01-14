from feeder.state import OverallState


def analyze_query_results(state: OverallState) -> OverallState:
    """Analyzes query results and flags queries that need optimization."""

    if not state.query_results:
        return state
    
    for result in state.query_results.results:
        if result.count == 0