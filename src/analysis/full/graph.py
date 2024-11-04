from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.configuration import Configuration
from analysis.full.state import InputGraphState, MainGraphState
from analysis.nodes.location import node_location
from analysis.nodes.profile_metadata import get_profile_metadata
from analysis.nodes.synthesis import node_synthesis
from analysis.sub_graph.criterion_analysis.graph import get_criterion_analysis_subgraph
from analysis.sub_graph.infer_enrichment.graph import get_infer_enrichment_subgraph
from analysis.sub_graph.web_enrichment.graph import get_web_enrichment_subgraph
from utils import get_retry_policy


def compute_profile_metadata(state: MainGraphState) -> MainGraphState:
    """Compute the profile metadata."""
    profile = get_profile_metadata(state.profile)
    return {"profile": profile}


def continue_to_analysis(state: MainGraphState):
    """Continue to the analysis graph."""
    return [
        Send(
            "criterion_analysis",
            {"main_state": state, "messages": [], "criterion": criterion},
        )
        for criterion in state.scorecard.criteria
    ]


def init_analysis(state: MainGraphState) -> MainGraphState:
    """BLANK : Initialize the analysis graph."""
    return {"scored_criterion": []}


def compile_analysis_full_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("compute_profile_metadata", compute_profile_metadata)
    workflow.add_node("node_location", node_location, retry=get_retry_policy())

    workflow.add_node(
        "criterion_analysis",
        get_criterion_analysis_subgraph(),
    )

    workflow.add_node(
        "web_enrichment",
        get_web_enrichment_subgraph(),
    )

    workflow.add_node(
        "infer_enrichment",
        get_infer_enrichment_subgraph(),
    )

    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node("node_synthesis", node_synthesis, retry=get_retry_policy())

    workflow.add_edge(START, "compute_profile_metadata")
    workflow.add_conditional_edges(
        "node_location",
        lambda x: ["web_enrichment", "infer_enrichment"]
        if x["location_analysis"] in ["GO", "DOUBT"]
        else ["__end__"],
        ["web_enrichment", "infer_enrichment", "__end__"],
    )
    workflow.add_edge("compute_profile_metadata", "node_location")
    workflow.add_edge("node_location", "web_enrichment")
    workflow.add_edge("node_location", "infer_enrichment")
    workflow.add_edge(
        [
            "web_enrichment",
            "infer_enrichment",
        ],
        "init_analysis",
    )

    workflow.add_conditional_edges(
        "init_analysis", continue_to_analysis, ["criterion_analysis"]
    )
    workflow.add_edge("criterion_analysis", "node_synthesis")
    workflow.add_edge("node_synthesis", END)

    graph = workflow.compile()
    graph.name = "AnalysisFullGraph"
    return graph
