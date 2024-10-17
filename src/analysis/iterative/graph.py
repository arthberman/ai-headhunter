from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.state import MainGraphState
from analysis.iterative.configuration import Configuration
from analysis.iterative.state import InputGraphState
from analysis.nodes.analysis_subgraph.graph import get_analysis_subgraph
from analysis.nodes.analysis_subgraph.state import AnalysisMainState
from analysis.nodes.synthesis.node import node_synthesis
from utils import get_retry_policy


def continue_to_analysis(state: MainGraphState):
    """Continue to the analysis graph."""
    return [
        Send(
            "node_analysis",
            AnalysisMainState(main_state=state, messages=[], criterion=criterion),
        )
        for criterion in state.scorecard.criteria
    ]


def init_analysis(state: MainGraphState) -> MainGraphState:
    """BLANK : Initialize the analysis graph."""
    return state


def compile_analysis_iterative_graph() -> CompiledGraph:
    """Compile the iterate analysis graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node("node_analysis", get_analysis_subgraph(), input=AnalysisMainState)
    workflow.add_node("node_synthesis", node_synthesis, retry=get_retry_policy())

    workflow.add_edge(START, "init_analysis")

    workflow.add_conditional_edges(
        "init_analysis", continue_to_analysis, ["node_analysis"]
    )
    workflow.add_edge("node_analysis", "node_synthesis")
    workflow.add_edge("node_synthesis", END)

    graph = workflow.compile()
    graph.name = "IterativeAnalysisGraph"
    return graph
