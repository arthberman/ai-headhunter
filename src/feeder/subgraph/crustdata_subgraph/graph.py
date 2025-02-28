from langgraph.graph import START, StateGraph
from langgraph.graph.graph import CompiledGraph

from src.feeder.subgraph.crustdata_subgraph.state import CrustdataSubgraphState

from .nodes.create_queries import create_crustdata_queries


def create_crustdata_subgraph() -> CompiledGraph:
    """Create the CrustData subgraph."""
    graph = StateGraph(CrustdataSubgraphState)

    graph.add_node("create_queries", create_crustdata_queries)

    graph.add_edge(START, "create_queries")

    return graph.compile()
