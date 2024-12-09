from langgraph.graph import END, START, StateGraph

from matcher.configuration import Configuration
from matcher.sub_graph.infer_enrichment.nodes.culture import node_infer_culture
from matcher.sub_graph.infer_enrichment.nodes.employment_type import (
    node_infer_employment_type,
)
from matcher.sub_graph.infer_enrichment.nodes.industry_sector import (
    node_infer_industry_sector,
)
from matcher.sub_graph.infer_enrichment.nodes.language import node_infer_languages
from matcher.sub_graph.infer_enrichment.nodes.profile_age import (
    node_infer_age,
)
from matcher.sub_graph.infer_enrichment.state import (
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

    workflow.add_node("infer_culture", node_infer_culture, retry=get_retry_policy())
    workflow.add_node("infer_languages", node_infer_languages, retry=get_retry_policy())
    workflow.add_node(
        "infer_industry_sector",
        node_infer_industry_sector,
        retry=get_retry_policy(),
    )
    workflow.add_node(
        "infer_employment_type",
        node_infer_employment_type,
        retry=get_retry_policy(),
    )
    workflow.add_node("infer_age", node_infer_age, retry=get_retry_policy())

    workflow.add_edge(START, "infer_employment_type")
    workflow.add_edge("infer_employment_type", "infer_age")
    workflow.add_edge("infer_age", "infer_languages")
    workflow.add_edge("infer_age", "infer_industry_sector")
    workflow.add_edge("infer_age", "infer_culture")
    workflow.add_edge("infer_languages", END)
    workflow.add_edge("infer_industry_sector", END)
    workflow.add_edge("infer_culture", END)

    # Compile the graph
    graph = workflow.compile()
    graph.name = "InferEnrichmentSubGraph"
    return graph
