from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from src.feeder.state import OverallState
from src.feeder.subgraph.location.nodes.find_locations_to_search import (
    find_locations_to_search,
)
from src.feeder.subgraph.location.nodes.get_location import get_location
from src.feeder.subgraph.location.nodes.get_relevant_locations_for_search import (
    get_relevant_locations_for_search,
)
from src.feeder.subgraph.location.state import (
    LocationSubGraphInputState,
    LocationSubGraphState,
)
from src.feeder.utils.retry_policy import get_retry_policy


def compile_location_subgraph() -> CompiledGraph:
    """Compile location processing pipeline.

    Processing Flow:
    1. get_location: LLM extracts & normalizes location from description
    2. find_locations_to_search: Retrieves location IDs from cache/API
    3. get_relevant_locations_for_search: LLM filters & ranks locations

    Retry Policy:
    - Applied to LLM operations (get_location, get_relevant_locations)
    - Not needed for deterministic cache/API lookup
    """
    subgraph_builder = StateGraph(
        LocationSubGraphState,
        input=LocationSubGraphInputState,
        output=OverallState,
    )
    # add nodes
    subgraph_builder.add_node("get_location", get_location, retry=get_retry_policy())
    subgraph_builder.add_node("find_locations_to_search", find_locations_to_search)
    subgraph_builder.add_node(
        "get_relevant_locations_for_search",
        get_relevant_locations_for_search,
        retry=get_retry_policy(),
    )
    # add edges
    subgraph_builder.add_edge(START, "get_location")
    subgraph_builder.add_edge("get_location", "find_locations_to_search")
    subgraph_builder.add_edge(
        "find_locations_to_search", "get_relevant_locations_for_search"
    )
    subgraph_builder.add_edge("get_relevant_locations_for_search", END)

    location_subgraph = subgraph_builder.compile()
    location_subgraph.name = "location_subgraph"
    return location_subgraph
