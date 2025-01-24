from langgraph.types import Command

from src.feeder.subgraph.query_optimization.nodes.apply_strategy import apply_strategy
from src.feeder.subgraph.query_optimization.state import QueryOptimizationState


def optimize_low_results(state: QueryOptimizationState):
    """Optimize queries with zero or low results."""
    if state.current_query_index is None:
        raise ValueError("current_query_index must be defined")

    if not state.query_results:
        raise ValueError("query_results must be defined")

    current_query = state.query_results[state.current_query_index]

    if not current_query.is_optimized:
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

    command = Command(
        graph=Command.PARENT,
        update={"query_results": state.query_results},
        goto="get_search_count",
    )
    return command
