from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.subgraph.reprocess_raw_query.nodes.combine_raw_query import (
    combine_raw_query,
)
from feeder.subgraph.reprocess_raw_query.nodes.split_raw_in_job_titles import (
    split_raw_in_job_titles,
)
from feeder.subgraph.reprocess_raw_query.nodes.split_raw_keywords import (
    split_raw_keywords,
)
from feeder.subgraph.reprocess_raw_query.nodes.split_raw_not_in_job_titles import (
    split_raw_not_in_job_titles,
)
from feeder.subgraph.reprocess_raw_query.state import (
    ReprocessRawQueryInputState,
    ReprocessRawQueryOutputState,
    ReprocessRawQueryState,
)


def create_reprocess_raw_query_graph() -> CompiledGraph:
    """Create graph for reprocess raw query."""
    subgraph_builder = StateGraph(
        ReprocessRawQueryState,
        input=ReprocessRawQueryInputState,
        output=ReprocessRawQueryOutputState,
    )

    subgraph_builder.add_node("split_raw_keywords", split_raw_keywords)
    subgraph_builder.add_node("split_raw_in_job_titles", split_raw_in_job_titles)
    subgraph_builder.add_node(
        "split_raw_not_in_job_titles", split_raw_not_in_job_titles
    )
    subgraph_builder.add_node("combine_raw_query", combine_raw_query)

    subgraph_builder.add_edge(START, "split_raw_keywords")
    subgraph_builder.add_edge(START, "split_raw_in_job_titles")
    subgraph_builder.add_edge(START, "split_raw_not_in_job_titles")
    subgraph_builder.add_edge("split_raw_keywords", "combine_raw_query")
    subgraph_builder.add_edge("split_raw_in_job_titles", "combine_raw_query")
    subgraph_builder.add_edge("split_raw_not_in_job_titles", "combine_raw_query")

    subgraph_builder.add_edge("combine_raw_query", END)

    reprocess_raw_query_graph = subgraph_builder.compile()
    reprocess_raw_query_graph.name = "reprocess_raw_query_subgraph"

    return reprocess_raw_query_graph
