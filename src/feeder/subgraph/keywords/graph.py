from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.state import OverallState

# from feeder.subgraph.keywords.nodes.apply_changes_keywords import (
#     apply_changes_keywords,
# )
from feeder.subgraph.keywords.nodes.judge_existing_keywords import (
    judge_existing_keywords,
)
from feeder.subgraph.keywords.state import (
    KeywordsInputState,
    KeywordsState,
)


def compile_keywords_subgraph() -> CompiledGraph:
    """Compile the keywords subgraph."""
    subgraph_builder = StateGraph(
        KeywordsState, input=KeywordsInputState, output=OverallState
    )
    subgraph_builder.add_node("judge_existing_keywords", judge_existing_keywords)
    # subgraph_builder.add_node("apply_changes_keywords", apply_changes_keywords)

    subgraph_builder.add_edge(START, "judge_existing_keywords")
    subgraph_builder.add_edge("judge_existing_keywords", END)
    # subgraph_builder.add_edge("judge_existing_keywords", "apply_changes_keywords")
    # subgraph_builder.add_edge("apply_changes_keywords", END)

    keywords_subgraph = subgraph_builder.compile()
    keywords_subgraph.name = "keywords_subgraph"
    return keywords_subgraph
