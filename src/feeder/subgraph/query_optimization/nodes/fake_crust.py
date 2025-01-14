from langgraph.types import Command

from feeder.subgraph.query_optimization.state import QueryOptimizationState


def fake_crust(state: QueryOptimizationState):
    """Handle query optimization including branched queries."""
    current_query_index = state.current_query_index

    if current_query_index >= len(state.query_results.results):
        return Command(
            graph=Command.PARENT,
            update={"current_query_index": current_query_index},
            goto="results_synthesizer",
        )

    current_query = state.query_results.results[current_query_index]

    # Check if current query has child queries that need processing
    if current_query.child_queries:
        # Add child queries to main results list
        state.query_results.results.extend(current_query.child_queries)
        current_query.child_queries = []  # Clear after moving
        current_query.is_optimized = True  # Mark parent as optimized

        # Move to next query
        current_query_index += 1
        return Command(
            graph=Command.PARENT,
            update={
                "current_query_index": current_query_index,
                "query_results": state.query_results,
            },
            goto="get_search_count",
        )

    # Regular optimization logic for single query
    latest_count = current_query.iterations[-1].count

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
