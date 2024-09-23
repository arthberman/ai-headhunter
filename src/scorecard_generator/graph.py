from langgraph.graph import END, START, StateGraph

from scorecard_generator.nodes.node_generate_context import node_generate_context
from scorecard_generator.nodes.node_generate_questions import node_generate_questions
from scorecard_generator.nodes.node_generate_scoring_distribution import (
    node_generate_scoring_distribution,
)
from scorecard_generator.nodes.node_synthesis import node_synthesis
from scorecard_generator.state import ScorecardGraphState, ScorecardInputGraphState
from scorecard_generator.sub_graph.enrichment.graph import get_enrichment_graph
from scorecard_generator.sub_graph.structure.graph import create_structure_graph


def compile_scorecard_generator_graph() -> StateGraph:
    """Compile the scorecard generator graph."""
    workflow = StateGraph(ScorecardGraphState, input=ScorecardInputGraphState)

    # Add nodes to the graph
    workflow.add_node("enrichment", get_enrichment_graph())
    workflow.add_node("generate_questions", node_generate_questions)
    workflow.add_node("generate_context", node_generate_context)
    workflow.add_node(
        "generate_scoring_distribution", node_generate_scoring_distribution
    )
    workflow.add_node("node_synthesis", node_synthesis)
    workflow.add_node("structure", create_structure_graph())

    # Define the edges
    workflow.add_edge(START, "node_synthesis")
    workflow.add_edge("node_synthesis", "enrichment")
    workflow.add_edge("enrichment", "generate_questions")
    workflow.add_edge("generate_questions", "structure")
    workflow.add_edge("structure", "generate_context")
    workflow.add_edge("generate_context", "generate_scoring_distribution")
    workflow.add_edge("generate_scoring_distribution", END)

    graph = workflow.compile()
    graph.name = "ScorecardGeneratorGraph"
    return graph
