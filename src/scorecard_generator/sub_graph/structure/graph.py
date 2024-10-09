from langgraph.graph import END, START, StateGraph

from scorecard_generator.sub_graph.structure.nodes import (
    apply_replacements,
    generate_scorecard_structure,
    iterate_scorecard_structure,
    judge_scorecard_structure,
)
from scorecard_generator.sub_graph.structure.state import StructureGraphState


def create_structure_graph() -> StateGraph:
    """Create the structure graph."""
    workflow = StateGraph(StructureGraphState)

    # Add nodes to the graph
    workflow.add_node("generate_scorecard_structure", generate_scorecard_structure)
    workflow.add_node("judge_scorecard_structure", judge_scorecard_structure)
    workflow.add_node("apply_structure_replacements", apply_replacements)
    workflow.add_node("iterate_scorecard_structure", iterate_scorecard_structure)

    # Define the edges
    workflow.add_conditional_edges(
        START,
        lambda x: x.scorecard is None,
        {True: "generate_scorecard_structure", False: "iterate_scorecard_structure"},
    )
    workflow.add_edge("generate_scorecard_structure", "judge_scorecard_structure")
    workflow.add_edge("iterate_scorecard_structure", "apply_structure_replacements")

    workflow.add_edge("judge_scorecard_structure", "apply_structure_replacements")

    # workflow.add_edge("apply_structure_replacements", "judge_scorecard_structure")
    workflow.add_edge("apply_structure_replacements", END)

    """ workflow.add_conditional_edges(
        "judge_scorecard_structure",
        lambda x: x.is_structure_valid or x.recursion_count >= 3,
        {True: END, False: "apply_structure_replacements"},
    ) """

    # workflow.add_edge("apply_structure_replacements", "judge_scorecard_structure")

    graph = workflow.compile()
    graph.name = "StructureSubGraph"
    return graph
