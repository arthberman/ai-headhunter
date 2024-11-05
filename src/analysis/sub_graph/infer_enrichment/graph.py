from langgraph.graph import END, START, StateGraph

from analysis.full.configuration import Configuration
from analysis.sub_graph.infer_enrichment.nodes.culture import node_infer_culture
from analysis.sub_graph.infer_enrichment.nodes.employment_type import (
    node_infer_employment_type,
)
from analysis.sub_graph.infer_enrichment.nodes.language import node_infer_languages
from analysis.sub_graph.infer_enrichment.nodes.profile_age import (
    node_infer_age,
)
from analysis.sub_graph.infer_enrichment.nodes.sector import node_infer_sector
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
        "node_infer_culture", node_infer_culture, retry=get_retry_policy()
    )
    workflow.add_node(
        "node_infer_languages", node_infer_languages, retry=get_retry_policy()
    )
    workflow.add_node("node_infer_sector", node_infer_sector, retry=get_retry_policy())
    workflow.add_node(
        "node_infer_employment_type",
        node_infer_employment_type,
        retry=get_retry_policy(),
    )
    workflow.add_node("node_infer_age", node_infer_age, retry=get_retry_policy())

    workflow.add_edge(START, "node_infer_employment_type")
    workflow.add_edge("node_infer_employment_type", "node_infer_age")
    workflow.add_edge("node_infer_age", "node_infer_languages")
    workflow.add_edge("node_infer_age", "node_infer_sector")
    workflow.add_edge("node_infer_age", "node_infer_culture")
    workflow.add_edge("node_infer_languages", END)
    workflow.add_edge("node_infer_sector", END)
    workflow.add_edge("node_infer_culture", END)

    # Compile the graph
    graph = workflow.compile()
    graph.name = "InferEnrichmentSubGraph"
    return graph
