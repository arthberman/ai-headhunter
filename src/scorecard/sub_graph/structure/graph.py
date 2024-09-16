from langgraph.graph import END, StateGraph, START
from scorecard.sub_graph.structure.state import StructureGraphState
from scorecard.sub_graph.structure.nodes import (
    generate_scorecard_structure,
    judge_scorecard_structure,
    apply_replacements,
)


def create_structure_graph() -> StateGraph:
    workflow = StateGraph(StructureGraphState)

    # Add nodes to the graph
    workflow.add_node("generate_scorecard_structure", generate_scorecard_structure)
    workflow.add_node("judge_scorecard_structure", judge_scorecard_structure)
    workflow.add_node("apply_structure_replacements", apply_replacements)

    # Define the edges
    workflow.add_edge(START, "generate_scorecard_structure")
    workflow.add_edge("generate_scorecard_structure", "judge_scorecard_structure")

    workflow.add_conditional_edges(
        "judge_scorecard_structure",
        lambda x: x.is_structure_valid or x.recursion_count >= 3,
        {True: END, False: "apply_structure_replacements"},
    )

    workflow.add_edge("apply_structure_replacements", "judge_scorecard_structure")

    return workflow.compile()
