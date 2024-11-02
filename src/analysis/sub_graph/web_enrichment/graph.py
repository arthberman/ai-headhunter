from typing import Set

from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph

from analysis.full.configuration import Configuration
from analysis.sub_graph.web_enrichment.education import node_education_enrichment
from analysis.sub_graph.web_enrichment.experience import node_experience_enrichment
from analysis.sub_graph.web_enrichment.state import (
    MainEnrichmentState,
    OutputEnrichmentState,
)
from utils import get_retry_policy


def continue_to_education_enrichment(state: MainEnrichmentState):
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

        return enrichment_tasks if enrichment_tasks else END
    else:
        return END


def continue_to_experience_enrichment(state: MainEnrichmentState):
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

        return enrichment_tasks if enrichment_tasks else END
    else:
        return END


def get_web_enrichment_subgraph():
    """Get the web enrichment subgraph."""
    workflow = StateGraph(
        MainEnrichmentState,
        input=MainEnrichmentState,
        output=OutputEnrichmentState,
        config_schema=Configuration,
    )

    workflow.add_node(
        "node_education_enrichment", node_education_enrichment, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_experience_enrichment",
        node_experience_enrichment,
        retry=get_retry_policy(),
    )

    workflow.add_conditional_edges(
        START,
        continue_to_education_enrichment,
        ["node_education_enrichment", END],
    )
    workflow.add_conditional_edges(
        START,
        continue_to_experience_enrichment,
        ["node_experience_enrichment", END],
    )

    workflow.add_edge("node_experience_enrichment", END)
    workflow.add_edge("node_education_enrichment", END)

    # Compile the graph
    graph = workflow.compile()
    graph.name = "WebEnrichmentSubGraph"
    return graph
