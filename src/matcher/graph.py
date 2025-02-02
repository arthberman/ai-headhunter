from typing import List

from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.types import Send

from matcher.configuration import Configuration
from matcher.models.synthesis import SynthesisScore
from matcher.nodes.check_location import node_check_location
from matcher.nodes.write_memory import node_write_memory
from matcher.state import InputGraphState, MainGraphState
from matcher.sub_graph.criterion_matcher.graph import get_criterion_matcher_subgraph
from matcher.sub_graph.decision.graph import get_decision_subgraph
from matcher.sub_graph.infer_enrichment.graph import get_infer_enrichment_subgraph
from matcher.sub_graph.web_enrichment.graph import get_web_enrichment_subgraph
from setup.models.scorecard import Category, Priority
from utils import compute_must_score, get_retry_policy
from utils.get_profile_metadata import get_profile_metadata


def already_enriched(state: MainGraphState) -> bool:
    """Check if the state is already enriched."""
    # Check if all inferred fields are filled
    inferred_fields_filled = all(
        [
            state.inferred_languages is not None,
            state.inferred_industry_sector is not None,
            state.inferred_culture is not None,
            state.inferred_role_trajectory is not None,
        ]
    )

    # Get unique LinkedIn IDs from profile
    unique_education_ids = {
        edu.linkedin_id
        for edu in state.profile.educations
        if edu.linkedin_id is not None
    }
    unique_experience_ids = {
        exp.linkedin_id
        for exp in state.profile.experiences
        if exp.linkedin_id is not None
    }

    # Check if enrichments match the number of unique LinkedIn IDs
    education_enrichment_matches = len(state.education_enrichment) == len(
        unique_education_ids
    )
    experience_enrichment_matches = len(state.experience_enrichment) == len(
        unique_experience_ids
    )

    return (
        inferred_fields_filled
        and education_enrichment_matches
        and experience_enrichment_matches
    )


def compute_profile_metadata(state: MainGraphState) -> MainGraphState:
    """Compute the profile metadata."""
    profile = get_profile_metadata(state.profile)
    return {"profile": profile}


def pass_through_node(state: MainGraphState) -> MainGraphState:
    """Fake node."""
    pass


def continue_to_matcher(state: MainGraphState):
    """Continue to the matcher."""
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
        == SynthesisScore.REJECTED
    ):
        return "decision"

    if sends_preferred:
        return sends_preferred

    return "decision"


def continue_to_enrichment(state: MainGraphState):
    """Continue to the enrichment."""
    if state.synthesis_location.score in [SynthesisScore.REJECTED]:
        return END

    if already_enriched(state):
        return ["supervisor"]
    else:
        return ["enrich_from_web", "enrich_from_reasoning"]


def compile_matcher_graph() -> CompiledGraph:
    """Compile the candidate matcher graph."""
    workflow = StateGraph(
        MainGraphState, input=InputGraphState, config_schema=Configuration
    )

    workflow.add_node("compute_profile_metadata", compute_profile_metadata)
    workflow.add_node("check_location", node_check_location, retry=get_retry_policy())

    workflow.add_node(
        "score_preferred_criteria",
        get_criterion_matcher_subgraph(),
    )

    workflow.add_node(
        "score_required_criteria",
        get_criterion_matcher_subgraph(),
    )

    workflow.add_node(
        "enrich_from_web",
        get_web_enrichment_subgraph(),
    )

    workflow.add_node(
        "enrich_from_reasoning",
        get_infer_enrichment_subgraph(),
    )

    workflow.add_node("decision", get_decision_subgraph())

    workflow.add_node("supervisor", pass_through_node)
    workflow.add_node("write_memory", node_write_memory, retry=get_retry_policy())

    workflow.add_edge(START, "compute_profile_metadata")
    workflow.add_edge("compute_profile_metadata", "check_location")
    workflow.add_conditional_edges(
        "check_location",
        continue_to_enrichment,
        ["enrich_from_web", "enrich_from_reasoning", "supervisor", END],
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
        continue_to_matcher,
        [
            "score_required_criteria",
            "score_preferred_criteria",
            "decision",
            "write_memory",
        ],
    )

    workflow.add_edge("score_required_criteria", "supervisor")
    workflow.add_edge("score_preferred_criteria", "supervisor")
    workflow.add_edge("write_memory", "supervisor")

    workflow.add_edge("decision", END)

    graph = workflow.compile()
    graph.name = "AnalysisFullGraph"
    return graph
