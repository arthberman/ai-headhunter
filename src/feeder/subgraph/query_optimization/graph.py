from langgraph.graph import START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.subgraph.query_optimization.nodes.check_query_status import (
    check_query_status,
)
from feeder.subgraph.query_optimization.nodes.fake_crust import fake_crust
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
    subgraph_builder.add_node("optimize_low_results", optimize_low_results)
    subgraph_builder.add_node("optimize_high_results", optimize_high_results)
    subgraph_builder.add_node("fake_crust", fake_crust)
    # add edges
    subgraph_builder.add_edge(START, "fake_crust")
    subgraph_builder.add_conditional_edges(
        "fake_crust",
        check_query_status,
        ["optimize_low_results", "optimize_high_results"],
    )
    optimization_subgraph = subgraph_builder.compile()
    optimization_subgraph.name = "optimization_subgraph"
    return optimization_subgraph
