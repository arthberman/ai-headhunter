from langgraph.graph import END, START, StateGraph

from scorecard.nodes import (
    get_enrichment_graph,
    node_context,
    node_job_posting,
    node_judge_scorecard_structure,
    node_questions,
    node_scorecard_structure,
    node_scoring_distribution,
    node_synthesis,
)
from scorecard.state import ScorecardGraphState, ScorecardInputGraphState
from utils import get_retry_policy


def compile_scorecard_graph() -> StateGraph:
    """Compile the scorecard full graph."""
    workflow = StateGraph(ScorecardGraphState, input=ScorecardInputGraphState)

    # Add nodes to the graph
    workflow.add_node("enrichment", get_enrichment_graph())
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
    # workflow.add_node("judge_structure", node_judge_scorecard_structure)
    # Define the edges
    workflow.add_edge(START, "enrichment")
    workflow.add_edge("enrichment", "generate_job_posting")
    workflow.add_edge("generate_job_posting", "generate_questions")
    workflow.add_edge("generate_questions", "generate_synthesis")
    workflow.add_edge("generate_synthesis", "generate_structure")
    # workflow.add_edge("generate_structure", "judge_structure")
    workflow.add_edge("generate_structure", "generate_context")
    workflow.add_edge("generate_context", "generate_scoring_distribution")
    workflow.add_edge("generate_scoring_distribution", END)

    graph = workflow.compile()
    graph.name = "ScorecardGraph"
    return graph
