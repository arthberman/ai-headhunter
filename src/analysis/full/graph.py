from typing import Set

from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.configuration import Configuration
from analysis.full.state import InputGraphState, MainGraphState
from analysis.nodes.analysis_subgraph.graph import get_analysis_subgraph
from analysis.nodes.candidate.culture import node_analysis_culture
from analysis.nodes.candidate.employment_type import node_find_employment_type
from analysis.nodes.candidate.language import node_language_enrichment
from analysis.nodes.candidate.profile_age import node_estimate_profile_age
from analysis.nodes.candidate.profile_metadata import get_profile_metadata
from analysis.nodes.candidate.sector import node_analysis_sector
from analysis.nodes.enrichment.education import node_education_enrichment
from analysis.nodes.enrichment.experience import node_experience_enrichment
from analysis.nodes.synthesis.node import node_synthesis
from utils import get_retry_policy


def continue_to_education_enrichment(state: MainGraphState):
    """Continue to education enrichment."""
    if state.profile.educations:
        # Use a set to keep track of unique (school, linkedin_url) pairs
        unique_schools: Set[tuple] = set()
        enrichment_tasks = []

        for e in state.profile.educations:
            school_key = (e.school, e.linkedin_url)
            if school_key not in unique_schools:
                unique_schools.add(school_key)
                enrichment_tasks.append(
                    Send(
                        "node_education_enrichment",
                        {"education": e},
                    )
                )

        return enrichment_tasks if enrichment_tasks else "init_analysis"
    else:
        return "init_analysis"


def continue_to_experience_enrichment(state: MainGraphState):
    """Continue to experience enrichment."""
    if state.profile.experiences:
        # Use a set to keep track of unique (company, linkedin_url) pairs
        unique_companies: Set[tuple] = set()
        enrichment_tasks = []

        for e in state.profile.experiences:
            company_key = (e.company, e.linkedin_url)
            if company_key not in unique_companies:
                unique_companies.add(company_key)
                enrichment_tasks.append(
                    Send(
                        "node_experience_enrichment",
                        {"experience": e},
                    )
                )

        return enrichment_tasks if enrichment_tasks else "init_analysis"
    else:
        return "init_analysis"


def init_node(state: MainGraphState) -> MainGraphState:
    """Initialize the graph."""
    profile = get_profile_metadata(state.profile)
    return {"profile": profile}


def continue_to_analysis(state: MainGraphState):
    """Continue to the analysis graph."""
    return [
        Send(
            "node_analysis",
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
        "node_language_enrichment", node_language_enrichment, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_education_enrichment", node_education_enrichment, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_experience_enrichment",
        node_experience_enrichment,
        retry=get_retry_policy(),
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
        "node_analysis",
        get_analysis_subgraph(),
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

    workflow.add_conditional_edges(
        "init_node",
        continue_to_education_enrichment,
        ["node_education_enrichment", "init_analysis"],
    )
    workflow.add_conditional_edges(
        "init_node",
        continue_to_experience_enrichment,
        ["node_experience_enrichment", "init_analysis"],
    )
    workflow.add_edge("init_node", "node_language_enrichment")
    workflow.add_edge("init_node", "node_find_employment_type")
    workflow.add_edge("init_node", "node_analysis_sector")
    workflow.add_edge("init_node", "node_analysis_culture")
    workflow.add_edge("node_find_employment_type", "node_estimate_profile_age")
    workflow.add_edge(
        [
            "node_experience_enrichment",
            "node_education_enrichment",
            "node_language_enrichment",
            "node_estimate_profile_age",
            "node_analysis_sector",
            "node_analysis_culture",
        ],
        "init_analysis",
    )

    workflow.add_conditional_edges(
        "init_analysis", continue_to_analysis, ["node_analysis"]
    )
    workflow.add_edge("node_analysis", "node_synthesis")
    workflow.add_edge("node_synthesis", END)

    graph = workflow.compile()
    graph.name = "AnalysisFullGraph"
    return graph
