from langgraph.graph import START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.nodes.classify_job_titles import classify_job_titles
from feeder.nodes.classify_keywords import classify_keywords
from feeder.nodes.create_queries import create_queries
from feeder.nodes.feedback_router import feedback_router
from feeder.nodes.first_gen_french_raw_query import first_gen_french_raw_query
from feeder.nodes.first_gen_raw_query import first_gen_raw_query
from feeder.nodes.get_search_count import node_get_search_count
from feeder.nodes.query_synthesizer import results_synthesizer
from feeder.state import OverallInputState, OverallOutputState, OverallState
from feeder.subgraph.in_job_titles.graph import compile_new_job_titles_subgraph
from feeder.subgraph.keywords.graph import compile_keywords_subgraph
from feeder.subgraph.location.graph import compile_location_subgraph
from feeder.subgraph.not_in_job_titles.graph import (
    compile_not_in_job_titles_subgraph,
)
from feeder.subgraph.query_optimization.graph import compile_optimization_subgraph
from feeder.utils.retry_policy import get_retry_policy


# only used to link subgraphs together
def pass_through_node(state: OverallState):
    """Fake node."""
    pass


def compile_feeder_graph() -> CompiledGraph:
    """Compile the feeder graph."""
    workflow = StateGraph(
        OverallState, input=OverallInputState, output=OverallOutputState
    )
    # add nodes
    workflow.add_node("fake_node_1", pass_through_node)
    workflow.add_node("fake_node_2", pass_through_node)
    workflow.add_node("fake_node_3", pass_through_node)
    workflow.add_node(
        "first_gen_JSON_object", first_gen_raw_query, retry=get_retry_policy()
    )
    workflow.add_node(
        "first_gen_french_raw_query",
        first_gen_french_raw_query,
        retry=get_retry_policy(),
    )
    workflow.add_node("location_subgraph", compile_location_subgraph())
    workflow.add_node("new_job_titles_subgraph", compile_new_job_titles_subgraph())
    workflow.add_node("new_keywords_subgraph", compile_keywords_subgraph())
    workflow.add_node(
        "new_not_in_job_titles_subgraph", compile_not_in_job_titles_subgraph()
    )
    workflow.add_node(
        "classify_job_titles", classify_job_titles, retry=get_retry_policy()
    )
    workflow.add_node("classify_keywords", classify_keywords, retry=get_retry_policy())
    workflow.add_node("create_queries", create_queries)
    workflow.add_node("get_search_count", node_get_search_count)
    workflow.add_node("optimization_subgraph", compile_optimization_subgraph())
    workflow.add_node("results_synthesizer", results_synthesizer)
    workflow.add_node("feedback_router", feedback_router)

    # add edges
    workflow.add_edge(START, "first_gen_JSON_object")
    workflow.add_edge("first_gen_JSON_object", "first_gen_french_raw_query")
    workflow.add_edge("first_gen_french_raw_query", "location_subgraph")
    workflow.add_edge("location_subgraph", "fake_node_1")
    workflow.add_edge("fake_node_1", "new_job_titles_subgraph")
    workflow.add_edge("new_job_titles_subgraph", "fake_node_2")
    workflow.add_edge("fake_node_2", "new_not_in_job_titles_subgraph")
    workflow.add_edge("new_not_in_job_titles_subgraph", "fake_node_3")
    workflow.add_edge("fake_node_3", "new_keywords_subgraph")
    workflow.add_edge("new_keywords_subgraph", "classify_job_titles")
    workflow.add_edge("new_keywords_subgraph", "classify_keywords")
    workflow.add_edge(["classify_job_titles", "classify_keywords"], "create_queries")
    workflow.add_edge("create_queries", "get_search_count")
    workflow.add_edge("get_search_count", "optimization_subgraph")

    workflow.add_edge("results_synthesizer", "feedback_router")

    graph = workflow.compile()
    graph.name = "feeder"
    return graph
