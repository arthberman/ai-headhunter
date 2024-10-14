from langgraph.graph import END, START, StateGraph

from scorecard.full.nodes import (
    generate_context,
    generate_job_posting,
    generate_questions,
    generate_scoring_distribution,
    generate_synthesis,
)
from scorecard.full.state import ScorecardGraphState, ScorecardInputGraphState
from scorecard.full.utils import get_retry_policy
from scorecard.nodes.enrichment_subgraph.graph import get_enrichment_graph
from scorecard.nodes.structure_subgraph.graph import create_structure_graph


def compile_scorecard_full_graph() -> StateGraph:
    """Compile the scorecard full graph."""
    workflow = StateGraph(ScorecardGraphState, input=ScorecardInputGraphState)

    # Add nodes to the graph
    workflow.add_node("enrichment", get_enrichment_graph())
    workflow.add_node(
        "generate_job_posting", generate_job_posting, retry=get_retry_policy()
    )
    workflow.add_node(
        "generate_questions", generate_questions, retry=get_retry_policy()
    )
    workflow.add_node("generate_context", generate_context, retry=get_retry_policy())
    workflow.add_node(
        "generate_scoring_distribution",
        generate_scoring_distribution,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "generate_synthesis", generate_synthesis, retry=get_retry_policy()
    )
    workflow.add_node("generate_structure", create_structure_graph())

    # Define the edges
    workflow.add_edge(START, "enrichment")
    workflow.add_edge("enrichment", "generate_job_posting")
    workflow.add_edge("generate_job_posting", "generate_questions")
    workflow.add_edge("generate_questions", "generate_synthesis")
    workflow.add_edge("generate_synthesis", "generate_structure")
    workflow.add_edge("generate_structure", "generate_context")
    workflow.add_edge("generate_context", "generate_scoring_distribution")
    workflow.add_edge("generate_scoring_distribution", END)

    graph = workflow.compile()
    graph.name = "ScorecardFullGraph"
    return graph
