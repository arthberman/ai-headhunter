from langgraph.graph import END, START, StateGraph

from analysis.full.configuration import Configuration
from analysis.sub_graph.infer_enrichment.nodes import (
    node_infer_culture,
    node_infer_intent,
    node_infer_language,
    node_infer_sector,
)
from analysis.sub_graph.infer_enrichment.state import (
    MainEnrichmentState,
    OutputEnrichmentState,
)
from utils import get_retry_policy


def get_infer_enrichment_subgraph():
    """Get the infer enrichment subgraph."""
    workflow = StateGraph(
        MainEnrichmentState,
        input=MainEnrichmentState,
        output=OutputEnrichmentState,
        config_schema=Configuration,
    )

    workflow.add_node("node_infer_sector", node_infer_sector, retry=get_retry_policy())
    workflow.add_node(
        "node_infer_culture", node_infer_culture, retry=get_retry_policy()
    )
    workflow.add_node("node_infer_intent", node_infer_intent, retry=get_retry_policy())
    workflow.add_node(
        "node_infer_language", node_infer_language, retry=get_retry_policy()
    )

    # Compile the graph
    graph = workflow.compile()
    graph.name = "InferEnrichmentSubGraph"
    return graph
