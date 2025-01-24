from langgraph.types import Command

from feeder.subgraph.query_optimization.state import QueryOptimizationState


def fake_crust(state: QueryOptimizationState):
    """Handle query optimization including branched queries."""
    if state.current_query_index is None:
        raise ValueError("current_query_index must be defined")

    current_query_index = state.current_query_index

    if not state.query_results:
        raise ValueError("query_results must be defined")

    if current_query_index >= len(state.query_results):
        return Command(
            graph=Command.PARENT,
            update={"current_query_index": current_query_index},
            goto="results_synthesizer",
        )
    current_query = state.query_results[current_query_index]

    if not current_query.iterations:
        raise ValueError(f"Query at index {current_query_index} has no iterations")

    latest_count = current_query.iterations[-1].count
    if latest_count is None:
        raise ValueError(
            f"Latest iteration for query {current_query_index} has no count"
        )
    if len(current_query.iterations) > state.max_iterations:
        current_query_index += 1
        return Command(
            graph=Command.PARENT,
            update={"current_query_index": current_query_index},
            goto="get_search_count",
        )

    if current_query.is_optimized:
        current_query_index += 1
        return Command(
            graph=Command.PARENT,
            update={"current_query_index": current_query_index},
            goto="get_search_count",
        )

    if 30 <= latest_count <= 1000:
        current_query.is_optimized = True
        current_query_index += 1
        return Command(
            graph=Command.PARENT,
            update={
                "current_query_index": current_query_index,
                "query_results": state.query_results,
            },
            goto="get_search_count",
        )
