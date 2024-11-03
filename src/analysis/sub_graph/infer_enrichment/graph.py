from langgraph.graph import END, START, StateGraph

from analysis.full.configuration import Configuration
from analysis.sub_graph.infer_enrichment.nodes.culture import node_analysis_culture
from analysis.sub_graph.infer_enrichment.nodes.employment_type import (
    node_find_employment_type,
)
from analysis.sub_graph.infer_enrichment.nodes.language import node_analysis_language
from analysis.sub_graph.infer_enrichment.nodes.profile_age import (
    node_estimate_profile_age,
)
from analysis.sub_graph.infer_enrichment.nodes.sector import node_analysis_sector
from analysis.sub_graph.infer_enrichment.state import (
    MainInferEnrichmentState,
    OutputInferEnrichmentState,
)
from utils import get_retry_policy


def get_infer_enrichment_subgraph():
    """Get the infer enrichment subgraph."""
    workflow = StateGraph(
        MainInferEnrichmentState,
        input=MainInferEnrichmentState,
        output=OutputInferEnrichmentState,
        config_schema=Configuration,
    )

    workflow.add_node(
        "node_analysis_culture", node_analysis_culture, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_analysis_language", node_analysis_language, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_analysis_sector", node_analysis_sector, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_find_employment_type", node_find_employment_type, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_estimate_profile_age", node_estimate_profile_age, retry=get_retry_policy()
    )

    workflow.add_edge(START, "node_find_employment_type")
    workflow.add_edge("node_find_employment_type", "node_estimate_profile_age")
    workflow.add_edge("node_estimate_profile_age", "node_analysis_language")
    workflow.add_edge("node_estimate_profile_age", "node_analysis_sector")
    workflow.add_edge("node_estimate_profile_age", "node_analysis_culture")
    workflow.add_edge("node_analysis_language", END)
    workflow.add_edge("node_analysis_sector", END)
    workflow.add_edge("node_analysis_culture", END)

    # Compile the graph
    graph = workflow.compile()
    graph.name = "InferEnrichmentSubGraph"
    return graph
