from feeder.models.query_memory import QueryAttempt, QueryMemory
from feeder.state import OverallState


def results_synthesizer(state: OverallState) -> OverallState:
    """Synthesize results from the query optimization subgraph."""
    # Initialize memory if it doesn't exist
    if state.query_memory is None:
        memory = QueryMemory()
    else:
        memory = state.query_memory

    for query in state.query_results:
        # Only process completed queries
        if not query.is_complete:
            continue

        # Convert filters to query string representation
        query_str = str(query.original_filters)

        # Track optimization journey
        optimization_journey = []
        results_journey = []

        for iteration in query.iterations:
            results_journey.append(iteration.count)
            if iteration.strategy_used:
                optimization_journey.append(iteration.strategy_used)
                memory.update_optimization_stats(
                    strategy=iteration.strategy_used,
                    success=(30 <= iteration.count <= 1000),
                )

        # Create QueryAttempt
        final_count = results_journey[-1]
        if final_count == 0:
            final_status = "failed"
        elif final_count < 30:
            final_status = "too_few"
        elif final_count > 1000:
            final_status = "too_many"
        else:
            final_status = "success"

        attempt = QueryAttempt(
            query=query_str,
            optimization_journey=optimization_journey,
            results_journey=results_journey,
            final_status=final_status,
        )

        # Store all completed attempts appropriately
        if final_status in ["failed", "too_few", "too_many"]:
            memory.failed_attempts.append(attempt)
        else:  # success
            memory.successful_attempts.append(attempt)

    state.query_memory = memory
    return state
