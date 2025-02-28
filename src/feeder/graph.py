from langgraph.graph import START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.nodes.create_linkedin_recruiter_queries import (
    create_linkedin_recruiter_queries,
)
from src.feeder.nodes.classify_job_titles import classify_job_titles
from src.feeder.nodes.classify_keywords import classify_keywords
from src.feeder.nodes.create_queries import create_queries
from src.feeder.nodes.feedback_router import feedback_router
from src.feeder.nodes.generate_raw_query import generate_raw_query
from src.feeder.nodes.generate_raw_query_target_language import (
    generate_raw_query_target_language,
)
from src.feeder.nodes.get_relevant_location import get_relevant_location
from src.feeder.nodes.ingest_raw_job_description import ingest_raw_job_description
from src.feeder.nodes.query_synthesizer import results_synthesizer
from src.feeder.nodes.route_data_source import route_data_source
from src.feeder.state import OverallInputState, OverallOutputState, OverallState
from src.feeder.subgraph.process_in_job_titles.graph import (
    compile_new_job_titles_subgraph,
)
from src.feeder.subgraph.process_keywords.graph import compile_keywords_subgraph
from src.feeder.subgraph.process_not_in_job_titles.graph import (
    compile_not_in_job_titles_subgraph,
)
from src.feeder.subgraph.query_optimization.graph import compile_optimization_subgraph
from src.feeder.utils.retry_policy import get_retry_policy


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
    workflow.add_node(
        "ingest_raw_job_description",
        ingest_raw_job_description,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "generate_raw_query", generate_raw_query, retry=get_retry_policy()
    )
    workflow.add_node(
        "generate_raw_query_target_language",
        generate_raw_query_target_language,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "get_relevant_location", get_relevant_location, retry=get_retry_policy()
    )
    workflow.add_node(
        "process_in_job_titles_subgraph", compile_new_job_titles_subgraph()
    )
    workflow.add_node(
        "process_not_in_job_titles_subgraph",
        compile_not_in_job_titles_subgraph(),
    )
    workflow.add_node("process_keywords_subgraph", compile_keywords_subgraph())
    workflow.add_node("classify_job_titles", classify_job_titles)
    workflow.add_node("classify_keywords", classify_keywords)
    workflow.add_node("route_data_source", route_data_source)
    workflow.add_node("create_queries", create_queries)
    workflow.add_node(
        "create_linkedin_recruiter_queries", create_linkedin_recruiter_queries
    )
    workflow.add_node("fake_node_1", pass_through_node)
    workflow.add_node("optimization_subgraph", compile_optimization_subgraph())
    workflow.add_node("results_synthesizer", results_synthesizer)
    workflow.add_node("feedback_router", feedback_router)

    # add edges
    workflow.add_edge(START, "ingest_raw_job_description")
    workflow.add_edge("ingest_raw_job_description", "generate_raw_query")
    workflow.add_edge("generate_raw_query_target_language", "get_relevant_location")
    workflow.add_edge(
        "process_in_job_titles_subgraph", "process_not_in_job_titles_subgraph"
    )
    workflow.add_edge("process_not_in_job_titles_subgraph", "process_keywords_subgraph")
    workflow.add_edge("process_keywords_subgraph", "classify_keywords")
    workflow.add_edge("process_keywords_subgraph", "classify_job_titles")
    workflow.add_edge("classify_keywords", "route_data_source")
    workflow.add_edge("classify_job_titles", "route_data_source")
    workflow.add_edge("fake_node_1", "optimization_subgraph")
    workflow.add_edge("optimization_subgraph", "results_synthesizer")
    workflow.add_edge("results_synthesizer", "feedback_router")

    graph = workflow.compile()
    graph.name = "feeder"
    return graph
