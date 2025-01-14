from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.state import OverallState
from feeder.subgraph.location.nodes.find_locations_to_search import (
    find_locations_to_search,
)
from feeder.subgraph.location.nodes.get_location import get_location
from feeder.subgraph.location.nodes.get_relevant_locations_for_search import (
    get_relevant_locations_for_search,
)
from feeder.subgraph.location.state import (
    LocationSubGraphInputState,
    LocationSubGraphState,
)


def compile_location_subgraph() -> CompiledGraph:
    subgraph_builder = StateGraph(
        LocationSubGraphState,
        input=LocationSubGraphInputState,
        output=OverallState,
    )
    subgraph_builder.add_node("get_location", get_location)
    subgraph_builder.add_node("find_locations_to_search", find_locations_to_search)
    subgraph_builder.add_node(
        "get_relevant_locations_for_search", get_relevant_locations_for_search
    )

    subgraph_builder.add_edge(START, "get_location")
    subgraph_builder.add_edge("get_location", "find_locations_to_search")
    subgraph_builder.add_edge(
        "find_locations_to_search", "get_relevant_locations_for_search"
    )
    subgraph_builder.add_edge("get_relevant_locations_for_search", END)

    location_subgraph = subgraph_builder.compile()
    location_subgraph.name = "location_subgraph"
    return location_subgraph
