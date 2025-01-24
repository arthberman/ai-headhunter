from langgraph.graph import END, START, StateGraph

from setup.configuration import Configuration
from setup.nodes import (
    node_context,
    node_human_answer_questions,
    node_job_posting,
    node_questions,
    node_scorecard_structure,
    node_scoring_distribution,
    node_synthesis,
)
from setup.nodes.clean_resource import node_clean_resource
from setup.nodes.generate_feeder_input import node_generate_feeder_input
from setup.state import ScorecardGraphState, ScorecardInputGraphState
from utils import get_retry_policy


def compile_setup_graph() -> StateGraph:
    """Compile the setup full graph."""
    workflow = StateGraph(
        ScorecardGraphState,
        input=ScorecardInputGraphState,
        config_schema=Configuration,
    )

    workflow.add_node("clean_resource", node_clean_resource, retry=get_retry_policy())
    workflow.add_node(
        "generate_job_posting", node_job_posting, retry=get_retry_policy()
    )
    workflow.add_node("generate_questions", node_questions, retry=get_retry_policy())
    workflow.add_node("generate_context", node_context, retry=get_retry_policy())
    workflow.add_node(
        "generate_scoring_distribution",
        node_scoring_distribution,
        retry=get_retry_policy(),
    )
    workflow.add_node("generate_synthesis", node_synthesis, retry=get_retry_policy())
    workflow.add_node("generate_structure", node_scorecard_structure)
    workflow.add_node("human_answer_questions", node_human_answer_questions)
    workflow.add_node("generate_feeder_input", node_generate_feeder_input)

    workflow.add_edge(START, "clean_resource")
    workflow.add_edge("clean_resource", "generate_job_posting")
    workflow.add_edge("generate_job_posting", "generate_questions")
    workflow.add_edge("generate_questions", "human_answer_questions")
    workflow.add_edge("human_answer_questions", "generate_synthesis")
    workflow.add_edge("generate_synthesis", "generate_structure")
    workflow.add_edge("generate_structure", "generate_context")
    workflow.add_edge("generate_context", "generate_scoring_distribution")
    workflow.add_edge("generate_scoring_distribution", "generate_feeder_input")
    workflow.add_edge("generate_feeder_input", END)

    graph = workflow.compile()
    graph.name = "setup"
    return graph
