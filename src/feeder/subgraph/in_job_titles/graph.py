from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.subgraph.in_job_titles.nodes.apply_changes_job_titles import (
    apply_changes_job_titles,
)
from feeder.subgraph.in_job_titles.nodes.judge_existing_job_title import (
    judge_existing_job_title,
)
from feeder.subgraph.in_job_titles.state import (
    NewJobTitlesSubgraphInputState,
    NewJobTitlesSubgraphState,
)
from feeder.subgraph.not_in_job_titles.state import (
    JobsToExcludeInputState,
)


def compile_new_job_titles_subgraph() -> CompiledGraph:
    """Compile the new job titles subgraph."""
    subgraph_builder = StateGraph(
        NewJobTitlesSubgraphState,
        input=NewJobTitlesSubgraphInputState,
        output=JobsToExcludeInputState,
    )
    subgraph_builder.add_node("judge_existing_job_title", judge_existing_job_title)
    subgraph_builder.add_node("apply_changes_job_titles", apply_changes_job_titles)
    subgraph_builder.add_edge(START, "judge_existing_job_title")
    subgraph_builder.add_edge("judge_existing_job_title", "apply_changes_job_titles")
    subgraph_builder.add_edge("apply_changes_job_titles", END)

    new_job_titles_subgraph = subgraph_builder.compile()
    new_job_titles_subgraph.name = "new_job_titles_subgraph"
    return new_job_titles_subgraph
