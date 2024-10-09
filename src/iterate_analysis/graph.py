from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from iterate_analysis.analysis.graph import get_iterate_analysis_graph
from iterate_analysis.analysis.state import AnalysisMainState
from iterate_analysis.configuration import Configuration
from iterate_analysis.state import InputGraphState, MainGraphState
from iterate_analysis.synthesis.node import node_synthesis


def continue_to_analysis(state: MainGraphState):
    """Continue to the analysis graph."""
    all_criteria = (
        state.scorecard.must_have_criteria
        + state.scorecard.important_criteria
        + state.scorecard.nice_to_have_criteria
    )

    return [
        Send(
            "node_analysis",
            AnalysisMainState(main_state=state, messages=[], criterion=criterion),
        )
        for criterion in all_criteria
    ]


def init_analysis(state: MainGraphState) -> MainGraphState:
    """BLANK : Initialize the analysis graph."""
    return state


def compile_iterate_analysis_graph() -> CompiledGraph:
    """Compile the iterate analysis graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node(
        "node_analysis", get_iterate_analysis_graph(), input=AnalysisMainState
    )
    workflow.add_node("node_synthesis", node_synthesis)

    workflow.add_edge(START, "init_analysis")

    workflow.add_conditional_edges(
        "init_analysis", continue_to_analysis, ["node_analysis"]
    )
    workflow.add_edge("node_analysis", "node_synthesis")
    workflow.add_edge("node_synthesis", END)

    graph = workflow.compile()
    graph.name = "IterateAnalysisGraph"
    return graph
