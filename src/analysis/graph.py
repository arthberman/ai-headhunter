from typing import List

from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.configuration import Configuration
from analysis.models.synthesis import SynthesisScore
from analysis.nodes.assess_open_to_work import node_assess_open_to_work
from analysis.nodes.check_hierarchy import node_check_hierarchy
from analysis.nodes.check_location import node_check_location
from analysis.nodes.conclude import node_conclude
from analysis.nodes.synthetize_intent import node_synthetize_intent
from analysis.nodes.write_memory import node_write_memory
from analysis.state import InputGraphState, MainGraphState
from analysis.sub_graph.criterion_analysis.graph import get_criterion_analysis_subgraph
from analysis.sub_graph.infer_enrichment.graph import get_infer_enrichment_subgraph
from analysis.sub_graph.web_enrichment.graph import get_web_enrichment_subgraph
from scorecard.models.scorecard import Category, Priority
from utils import compute_must_score, get_retry_policy
from utils.get_profile_metadata import get_profile_metadata


def compute_profile_metadata(state: MainGraphState) -> MainGraphState:
    """Compute the profile metadata."""
    profile = get_profile_metadata(state.profile)
    return {"profile": profile}


def pass_through_node(state: MainGraphState) -> MainGraphState:
    """Fake node."""
    pass


def continue_to_analysis(state: MainGraphState):
    """Continue to the analysis."""
    # Get set of already processed criterion IDs
    processed_criterion_ids = {sc.id for sc in state.scored_criterion}

    sends_required: List[Send] = []
    for criterion in state.scorecard.criteria:
        if (
            criterion.priority == Priority.REQUIRED
            and criterion.category != Category.LOCATION
            and criterion.id not in processed_criterion_ids
        ):
            sends_required.append(
                Send(
                    "score_required_criteria",
                    {"main_state": state, "messages": [], "criterion": criterion},
                )
            )

    sends_preferred: List[Send] = []
    for criterion in state.scorecard.criteria:
        if (
            criterion.priority == Priority.PREFERRED
            and criterion.category != Category.LOCATION
            and criterion.id not in processed_criterion_ids
        ):
            sends_preferred.append(
                Send(
                    "score_preferred_criteria",
                    {"main_state": state, "messages": [], "criterion": criterion},
                )
            )

    if state.batch_store_ops:
        return ["write_memory"]

    if sends_required:
        return sends_required

    if (
        compute_must_score(state.scored_criterion, state.scorecard).score
        == SynthesisScore.FAIL
    ):
        return ["synthetize_scored_criteria"]

    if sends_preferred:
        return sends_preferred

    return ["synthetize_scored_criteria"]


def continue_to_enrichment(state: MainGraphState):
    """Continue to the enrichment."""
    if state.synthesis_location.score in [SynthesisScore.PASS, SynthesisScore.DOUBT]:
        return ["enrich_from_web", "enrich_from_reasoning"]

    return END


def compile_analysis_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("compute_profile_metadata", compute_profile_metadata)
    workflow.add_node("check_location", node_check_location, retry=get_retry_policy())

    workflow.add_node(
        "score_preferred_criteria",
        get_criterion_analysis_subgraph(),
    )

    workflow.add_node(
        "score_required_criteria",
        get_criterion_analysis_subgraph(),
    )

    workflow.add_node(
        "enrich_from_web",
        get_web_enrichment_subgraph(),
    )

    workflow.add_node(
        "enrich_from_reasoning",
        get_infer_enrichment_subgraph(),
    )

    workflow.add_node(
        "synthetize_intent", node_synthetize_intent, retry=get_retry_policy()
    )

    workflow.add_node("synthetize_scored_criteria", pass_through_node)

    workflow.add_node("supervisor", pass_through_node)
    workflow.add_node("write_memory", node_write_memory, retry=get_retry_policy())
    workflow.add_node("conclude", node_conclude, retry=get_retry_policy())

    workflow.add_node(
        "assess_open_to_work", node_assess_open_to_work, retry=get_retry_policy()
    )
    workflow.add_node("check_hierarchy", node_check_hierarchy, retry=get_retry_policy())

    workflow.add_edge(START, "compute_profile_metadata")
    workflow.add_edge("compute_profile_metadata", "check_location")
    workflow.add_conditional_edges(
        "check_location",
        continue_to_enrichment,
        ["enrich_from_web", "enrich_from_reasoning", END],
    )
    workflow.add_edge(
        [
            "enrich_from_web",
            "enrich_from_reasoning",
        ],
        "supervisor",
    )

    workflow.add_conditional_edges(
        "supervisor",
        continue_to_analysis,
        [
            "score_required_criteria",
            "score_preferred_criteria",
            "synthetize_scored_criteria",
            "write_memory",
        ],
    )

    workflow.add_edge("score_required_criteria", "supervisor")
    workflow.add_edge("score_preferred_criteria", "supervisor")
    workflow.add_edge("write_memory", "supervisor")

    workflow.add_edge("synthetize_scored_criteria", "assess_open_to_work")
    workflow.add_edge("synthetize_scored_criteria", "check_hierarchy")

    workflow.add_edge("check_hierarchy", "synthetize_intent")
    workflow.add_edge("assess_open_to_work", "synthetize_intent")

    workflow.add_edge("synthetize_intent", "conclude")
    workflow.add_edge("conclude", END)

    graph = workflow.compile()
    graph.name = "AnalysisFullGraph"
    return graph
