from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from src.feeder.state import OverallState
from src.feeder.subgraph.process_keywords.nodes.apply_changes_existing_keywords import (
    apply_changes_existing_keywords,
)
from src.feeder.subgraph.process_keywords.nodes.judge_existing_keywords import (
    judge_existing_keywords,
)
from src.feeder.subgraph.process_keywords.state import (
    KeywordsInputState,
    KeywordsState,
)
from src.feeder.utils.retry_policy import get_retry_policy


def compile_keywords_subgraph() -> CompiledGraph:
    """Compile the keywords subgraph.

    Processing flow:
    1. judge_existing_keywords: LLM judges existing keywords
    """
    subgraph_builder = StateGraph(
        KeywordsState, input=KeywordsInputState, output=OverallState
    )
    # add node
    subgraph_builder.add_node(
        "judge_existing_keywords",
        judge_existing_keywords,
        retry=get_retry_policy(),
    )
    subgraph_builder.add_node(
        "apply_changes_existing_keywords",
        apply_changes_existing_keywords,
        retry=get_retry_policy(),
    )
    # add edges
    subgraph_builder.add_edge(START, "judge_existing_keywords")
    subgraph_builder.add_edge(
        "judge_existing_keywords", "apply_changes_existing_keywords"
    )
    subgraph_builder.add_edge("apply_changes_existing_keywords", END)

    keywords_subgraph = subgraph_builder.compile()
    keywords_subgraph.name = "keywords_subgraph"
    return keywords_subgraph
