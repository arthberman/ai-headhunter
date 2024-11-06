from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.configuration import Configuration
from analysis.full.state import InputGraphState, MainGraphState
from analysis.models.synthesis import SynthesisScore
from analysis.nodes.match_location import node_synthesis_location
from analysis.nodes.profile_metadata import get_profile_metadata
from analysis.nodes.synthesis import node_synthesis_overall
from analysis.nodes.synthesis_must import node_synthesis_must
from analysis.sub_graph.criterion_analysis.graph import get_criterion_analysis_subgraph
from analysis.sub_graph.infer_enrichment.graph import get_infer_enrichment_subgraph
from analysis.sub_graph.web_enrichment.graph import get_web_enrichment_subgraph
from scorecard.models.scorecard import CriterionType, ImportanceLevel
from utils import get_retry_policy


def compute_profile_metadata(state: MainGraphState) -> MainGraphState:
    """Compute the profile metadata."""
    profile = get_profile_metadata(state.profile)
    return {"profile": profile}


def continue_to_nice_criteria(state: MainGraphState):
    """Continue to the nice criteria analysis."""
    if state.synthesis_must.score == SynthesisScore.FAIL:
        return ["node_synthesis_overall"]

    return [
        Send(
            "match_nice_criteria",
            {"main_state": state, "messages": [], "criterion": criterion},
        )
        for criterion in state.scorecard.criteria
        if criterion.importance_level == ImportanceLevel.NICE_TO_HAVE
        and criterion.type != CriterionType.LOCATION
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
        and criterion.type != CriterionType.LOCATION
    ]


def init_analysis(state: MainGraphState) -> MainGraphState:
    """Fake node."""
    pass


def compile_analysis_full_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("compute_profile_metadata", compute_profile_metadata)
    workflow.add_node(
        "node_synthesis_location", node_synthesis_location, retry=get_retry_policy()
    )

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

    workflow.add_node(
        "node_synthesis_must", node_synthesis_must, retry=get_retry_policy()
    )

    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node(
        "node_synthesis_overall", node_synthesis_overall, retry=get_retry_policy()
    )

    workflow.add_edge(START, "compute_profile_metadata")
    workflow.add_edge("compute_profile_metadata", "node_synthesis_location")
    workflow.add_conditional_edges(
        "node_synthesis_location",
        lambda state: (
            ["web_enrichment", "infer_enrichment"]
            if state.synthesis_location.score
            in [SynthesisScore.PASS, SynthesisScore.DOUBT]
            else ["node_synthesis_overall"]
        )
        if isinstance(state, MainGraphState)
        else [],
        ["web_enrichment", "infer_enrichment", "node_synthesis_overall"],
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

    workflow.add_edge("match_must_criteria", "node_synthesis_must")

    workflow.add_conditional_edges(
        "node_synthesis_must",
        continue_to_nice_criteria,
        ["match_nice_criteria", "node_synthesis_overall"],
    )
    workflow.add_edge("match_nice_criteria", "node_synthesis_overall")
    workflow.add_edge("node_synthesis_overall", END)

    graph = workflow.compile()
    graph.name = "AnalysisFullGraph"
    return graph
