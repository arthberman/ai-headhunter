from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.feedback.configuration import Configuration
from analysis.feedback.nodes import (
    node_extract_profile_related_elements,
    node_extract_scorecard_related_elements,
    node_reformulate_human_feedback,
    node_synthesize_feedback,
)
from analysis.feedback.state import InputGraphState, MainGraphState
from utils import get_retry_policy


def compile_analysis_feedback_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node(
        "node_reformulate_human_feedback",
        node_reformulate_human_feedback,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "node_extract_profile_related_elements",
        node_extract_profile_related_elements,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "node_extract_scorecard_related_elements",
        node_extract_scorecard_related_elements,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "node_synthesize_feedback",
        node_synthesize_feedback,
        retry=get_retry_policy(),
    )

    workflow.add_edge(START, "node_reformulate_human_feedback")
    workflow.add_edge(
        "node_reformulate_human_feedback", "node_extract_profile_related_elements"
    )
    workflow.add_edge(
        "node_extract_profile_related_elements",
        "node_extract_scorecard_related_elements",
    )
    workflow.add_edge(
        "node_extract_scorecard_related_elements", "node_synthesize_feedback"
    )
    workflow.add_edge("node_synthesize_feedback", END)

    graph = workflow.compile()
    graph.name = "AnalysisFeedbackGraph"
    return graph
