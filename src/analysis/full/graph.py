from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.configuration import Configuration
from analysis.full.state import InputGraphState, MainGraphState
from analysis.nodes.candidate.culture import node_analysis_culture
from analysis.nodes.candidate.employment_type import node_find_employment_type
from analysis.nodes.candidate.language import node_analysis_language
from analysis.nodes.candidate.profile_age import node_estimate_profile_age
from analysis.nodes.candidate.profile_metadata import get_profile_metadata
from analysis.nodes.candidate.sector import node_analysis_sector
from analysis.nodes.synthesis.node import node_synthesis
from analysis.sub_graph.criterion_analysis.graph import get_criterion_analysis_subgraph
from analysis.sub_graph.web_enrichment.graph import get_web_enrichment_subgraph
from utils import get_retry_policy


def init_node(state: MainGraphState) -> MainGraphState:
    """Initialize the graph."""
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
    return {"profile": state.profile}


def compile_analysis_full_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("init_node", init_node)
    workflow.add_node(
        "node_analysis_language", node_analysis_language, retry=get_retry_policy()
    )

    workflow.add_node(
        "node_find_employment_type",
        node_find_employment_type,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "node_estimate_profile_age",
        node_estimate_profile_age,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "criterion_analysis",
        get_criterion_analysis_subgraph(),
    )

    workflow.add_node(
        "web_enrichment",
        get_web_enrichment_subgraph(),
    )
    workflow.add_node(
        "node_analysis_sector", node_analysis_sector, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_analysis_culture", node_analysis_culture, retry=get_retry_policy()
    )
    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node("node_synthesis", node_synthesis, retry=get_retry_policy())

    workflow.add_edge(START, "init_node")

    workflow.add_edge("init_node", "node_analysis_language")
    workflow.add_edge("init_node", "node_find_employment_type")
    workflow.add_edge("init_node", "node_analysis_sector")
    workflow.add_edge("init_node", "node_analysis_culture")
    workflow.add_edge("init_node", "web_enrichment")
    workflow.add_edge("node_find_employment_type", "node_estimate_profile_age")
    workflow.add_edge(
        [
            "web_enrichment",
            "node_analysis_language",
            "node_estimate_profile_age",
            "node_analysis_sector",
            "node_analysis_culture",
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
