from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.store.base import BaseStore

from analysis.configuration import Configuration
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
        unique_urls = set()
        enrichment_tasks = []

        for education in state.profile.educations:
            if education.linkedin_url and education.linkedin_url not in unique_urls:
                unique_urls.add(education.linkedin_url)
                enrichment_tasks.append(
                    Send(
                        "node_education_enrichment",
                        {"education": education},
                    )
                )

        return enrichment_tasks if enrichment_tasks else "node_save_memory"
    return "node_save_memory"


def continue_to_experience_enrichment(state: MainEnrichmentState):
    """Continue to experience enrichment."""
    if state.profile.experiences:
        unique_urls = set()
        enrichment_tasks = []

        for experience in state.profile.experiences:
            if experience.linkedin_url and experience.linkedin_url not in unique_urls:
                unique_urls.add(experience.linkedin_url)
                enrichment_tasks.append(
                    Send(
                        "node_experience_enrichment",
                        {"experience": experience},
                    )
                )

        return enrichment_tasks if enrichment_tasks else "node_save_memory"
    return "node_save_memory"


def node_save_memory(
    state: MainEnrichmentState, *, store: BaseStore
) -> OutputEnrichmentState:
    """Save the memory."""
    if state.batch_store_ops:
        store.batch(state.batch_store_ops)

    pass


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

    workflow.add_node("node_save_memory", node_save_memory, retry=get_retry_policy())

    workflow.add_conditional_edges(
        START,
        continue_to_education_enrichment,
        ["node_education_enrichment", "node_save_memory"],
    )
    workflow.add_conditional_edges(
        START,
        continue_to_experience_enrichment,
        ["node_experience_enrichment", "node_save_memory"],
    )

    workflow.add_edge("node_experience_enrichment", "node_save_memory")
    workflow.add_edge("node_education_enrichment", "node_save_memory")
    workflow.add_edge("node_save_memory", END)

    # Compile the graph
    graph = workflow.compile()
    graph.name = "WebEnrichmentSubGraph"
    return graph
