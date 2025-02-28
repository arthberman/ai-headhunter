from langgraph.graph import START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.subgraph.query_optimization.nodes.analyze_current_query import (
    analyze_current_query,
)
from feeder.subgraph.query_optimization.nodes.optimize_high_results import (
    optimize_high_results,
)
from feeder.subgraph.query_optimization.nodes.optimize_low_results import (
    optimize_low_results,
)
from feeder.subgraph.query_optimization.state import (
    QueryOptimizationInputState,
    QueryOptimizationOutputState,
    QueryOptimizationState,
)


def compile_optimization_subgraph() -> CompiledGraph:
    """Create the query optimization workflow."""
    subgraph_builder = StateGraph(
        QueryOptimizationState,
        input=QueryOptimizationInputState,
        output=QueryOptimizationOutputState,
    )

    # add nodes
    subgraph_builder.add_node("analyze_current_query", analyze_current_query)
    subgraph_builder.add_node("optimize_low_results", optimize_low_results)
    subgraph_builder.add_node("optimize_high_results", optimize_high_results)

    # add edges
    subgraph_builder.add_edge(START, "analyze_current_query")

    optimization_subgraph = subgraph_builder.compile()
    optimization_subgraph.name = "query_optimization_subgraph"
    return optimization_subgraph
