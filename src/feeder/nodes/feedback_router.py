from typing import Literal

from langgraph.graph import END
from langgraph.types import Command

from feeder.state import OverallState
from src.feeder.utils.logger_setup import logger


def feedback_router(
    state: OverallState,
) -> Command[Literal["generate_raw_query", "__end__"]]:
    """Route based on query memory state."""
    try:
        if state.query_memory is None:
            return Command(goto=END)

        # Check if there are any failed or suboptimal queries
        has_failed = len(state.query_memory.failed_attempts) > 0
        total_attempts = len(state.query_memory.failed_attempts) + len(
            state.query_memory.successful_attempts
        )

        # If all queries were successful, end the process
        if total_attempts > 0 and not has_failed:
            return Command(goto=END)

        # Check if we should try another generation based on optimization results
        if state.query_results:
            incomplete_queries = [q for q in state.query_results if not q.is_complete]

            if not incomplete_queries:
                # All queries are complete, check if we need another generation
                optimization_stats = {
                    q.optimization_status: q.optimization_status
                    for q in state.query_results
                }

                # If we have any optimal results, end the process
                if "optimal" in optimization_stats:
                    return Command(goto=END)

                # Check global iteration count
                if not hasattr(state, "global_iteration_count"):
                    state.global_iteration_count = 0

                # Increment counter
                state.global_iteration_count += 1

                # If we've reached max generations, end the process
                if state.global_iteration_count > 2:
                    return Command(goto=END)

                # Try another generation
                return Command(
                    goto="generate_raw_query",
                    update={"global_iteration_count": state.global_iteration_count},
                )

        return Command(goto=END)
    except Exception as e:
        logger.error(f"Error in feedback_router: {e}")
        return Command(goto=END)
