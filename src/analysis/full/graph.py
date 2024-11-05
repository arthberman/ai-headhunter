from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.configuration import Configuration
from analysis.full.state import InputGraphState, MainGraphState
from analysis.models.location import LocationScore
from analysis.nodes.match_location import node_match_location
from analysis.nodes.profile_metadata import get_profile_metadata
from analysis.nodes.synthesis import node_synthesis
from analysis.nodes.synthesis_must import node_synthesis_must
from analysis.sub_graph.criterion_analysis.graph import get_criterion_analysis_subgraph
from analysis.sub_graph.infer_enrichment.graph import get_infer_enrichment_subgraph
from analysis.sub_graph.web_enrichment.graph import get_web_enrichment_subgraph
from scorecard.models.scorecard import ImportanceLevel
from utils import get_retry_policy


def compute_profile_metadata(state: MainGraphState) -> MainGraphState:
    """Compute the profile metadata."""
    profile = get_profile_metadata(state.profile)
    return {"profile": profile}


def continue_to_nice_criteria(state: MainGraphState):
    """Continue to the nice criteria analysis."""
    return [
        Send(
            "match_nice_criteria",
            {"main_state": state, "messages": [], "criterion": criterion},
        )
        for criterion in state.scorecard.criteria
        if criterion.importance_level == ImportanceLevel.NICE_TO_HAVE
    ]


def continue_to_must_criteria(state: MainGraphState):
    """Continue to the must criteria analysis."""
    return [
        Send(
            "match_must_criteria",
            {"main_state": state, "messages": [], "criterion": criterion},
        )
        for criterion in state.scorecard.criteria
        if criterion.importance_level == ImportanceLevel.MUST_HAVE
    ]


def continue_after_location(state: MainGraphState):
    """Continue after the location analysis."""
    if state.scored_location_criterion.score.value in [
        LocationScore.PASS,
        LocationScore.DOUBT,
    ]:
        return ["web_enrichment", "infer_enrichment"]
    else:
        return END


def node_test(state: MainGraphState):
    """Test node."""
    return {"scored_criterion": []}


def init_analysis(state: MainGraphState) -> MainGraphState:
    """BLANK : Initialize the analysis graph."""
    return {"scored_criterion": []}


def compile_analysis_full_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("compute_profile_metadata", compute_profile_metadata)
    workflow.add_node("match_location", node_match_location, retry=get_retry_policy())

    workflow.add_node(
        "match_nice_criteria",
        get_criterion_analysis_subgraph(),
    )

    workflow.add_node(
        "match_must_criteria",
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

    workflow.add_node("synthesis_must", node_synthesis_must, retry=get_retry_policy())

    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node("node_synthesis", node_synthesis, retry=get_retry_policy())

    workflow.add_edge(START, "compute_profile_metadata")
    workflow.add_edge("compute_profile_metadata", "match_location")
    workflow.add_conditional_edges(
        "match_location",
        continue_after_location,
        ["web_enrichment", "infer_enrichment", END],
    )
    workflow.add_edge(
        [
            "web_enrichment",
            "infer_enrichment",
        ],
        "init_analysis",
    )

    workflow.add_conditional_edges(
        "init_analysis", continue_to_must_criteria, ["match_must_criteria"]
    )

    workflow.add_edge("match_must_criteria", "synthesis_must")

    workflow.add_conditional_edges(
        "synthesis_must",
        continue_to_nice_criteria,
        ["match_nice_criteria", END],
    )
    workflow.add_edge("match_nice_criteria", "node_synthesis")
    workflow.add_edge("node_synthesis", END)

    graph = workflow.compile()
    graph.name = "AnalysisFullGraph"
    return graph
