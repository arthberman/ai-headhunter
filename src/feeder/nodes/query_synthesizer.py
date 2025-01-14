from feeder.models.query_memory import QueryAttempt, QueryMemory
from feeder.state import OverallState


def results_synthesizer(state: OverallState) -> OverallState:
    """Synthesize results from the query optimization subgraph."""
    # Initialize memory if it doesn't exist
    if state.query_memory is None:
        memory = QueryMemory()
    else:
        memory = state.query_memory

    for query in state.query_results.results:
        # Convert filters to query string representation
        query_str = str(query.original_filters)

        # Track optimization journey
        optimization_journey = []
        results_journey = []

        for iteration in query.iterations:
            results_journey.append(iteration.count)
            if iteration.strategy_used:
                optimization_journey.append(iteration.strategy_used)
                # Update optimization statistics
                if iteration.strategy_used not in memory.optimization_stats:
                    memory.optimization_stats[iteration.strategy_used] = {
                        "attempts": 0,
                        "successes": 0,
                    }
                memory.optimization_stats[iteration.strategy_used]["attempts"] += 1
                if 30 <= iteration.count <= 1000:
                    memory.optimization_stats[iteration.strategy_used]["successes"] += 1

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

        if final_count == 0:
            memory.failed_attempts.append(attempt)
        elif 30 <= final_count <= 1000:
            memory.successful_attempts.append(attempt)

    state.query_memory = memory
    return state
