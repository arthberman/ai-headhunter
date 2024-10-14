from typing import Set

from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from analysis.full.configuration import Configuration
from analysis.full.state import InputGraphState, MainGraphState
from analysis.full.utils import get_retry_policy
from analysis.nodes.analysis_subgraph.graph import get_analysis_subgraph
from analysis.nodes.career_path.analysis import node_career_path
from analysis.nodes.enrichment.education import node_education_enrichment
from analysis.nodes.enrichment.experience import node_experience_enrichment
from analysis.nodes.enrichment.language import node_language_enrichment
from analysis.nodes.synthesis.node import node_synthesis


def continue_to_school_enrichment(state: MainGraphState):
    """Continue to school enrichment."""
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


def continue_to_company_enrichment(state: MainGraphState):
    """Continue to company enrichment."""
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
    """Initialize the node."""
    return state


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
            {"main_state": state, "messages": [], "criterion": criterion},
        )
        for criterion in all_criteria
    ]


def init_analysis(state: MainGraphState) -> MainGraphState:
    """BLANK : Initialize the analysis graph."""
    return state


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
        "node_analysis",
        get_analysis_subgraph(),
    )
    workflow.add_node("node_career_path", node_career_path, retry=get_retry_policy())
    workflow.add_node("init_analysis", init_analysis)
    workflow.add_node("node_synthesis", node_synthesis, retry=get_retry_policy())

    workflow.add_edge(START, "init_node")

    workflow.add_conditional_edges(
        "init_node",
        continue_to_school_enrichment,
        ["node_education_enrichment", "init_analysis"],
    )
    workflow.add_conditional_edges(
        "init_node",
        continue_to_company_enrichment,
        ["node_experience_enrichment", "init_analysis"],
    )
    workflow.add_edge("init_node", "node_language_enrichment")
    workflow.add_edge("init_node", "node_career_path")
    workflow.add_edge(
        [
            "node_experience_enrichment",
            "node_education_enrichment",
            "node_language_enrichment",
            "node_career_path",
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
