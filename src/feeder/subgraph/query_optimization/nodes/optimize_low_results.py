from typing import Literal

from langgraph.types import Command

from feeder.subgraph.query_optimization.apply_strategy import apply_strategy
from src.feeder.subgraph.query_optimization.state import QueryOptimizationState
from src.feeder.utils.logger_setup import logger


def optimize_low_results(
    state: QueryOptimizationState,
) -> Command[Literal["analyze_current_query"]]:
    """Optimize queries with low results."""
    try:
        current_query = state.query_results[state.current_query_index]

        latest_filters = current_query.latest_filters
        next_strategy = current_query.get_next_strategy()

        if next_strategy:
            optimized_filters = apply_strategy(latest_filters, next_strategy, state)

            if optimized_filters:
                next_strategy.attempted = True
                current_query.optimization_attempt += 1
                current_query.add_iteration(
                    filters=optimized_filters,
                    profile_count=None,
                    optimization_reason=f"Applied {next_strategy.strategy_type} strategy",
                    strategy_used=next_strategy.strategy_type,
                )

            logger.info(
                f"Optimized query {state.current_query_index} with {next_strategy.strategy_type} strategy"
            )

            return Command(
                update={
                    "query_results": state.query_results,
                },
                goto="analyze_current_query",
            )
        else:
            logger.info(
                f"No more strategies to optimize query {state.current_query_index}. Moving to next query."
            )
            return Command(
                update={
                    "current_query_index": state.current_query_index + 1,
                },
                goto="analyze_current_query",
            )
    except Exception as e:
        logger.error(f"Error optimizing low results: {e}")
        raise e
