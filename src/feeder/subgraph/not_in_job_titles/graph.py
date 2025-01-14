from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from feeder.subgraph.keywords.state import KeywordsInputState
from feeder.subgraph.not_in_job_titles.nodes.apply_changes_not_in_job_titles import (
    apply_changes_not_in_job_titles,
)
from feeder.subgraph.not_in_job_titles.nodes.judge_existing_not_in_job_titles import (
    judge_existing_not_in_job_titles,
)
from feeder.subgraph.not_in_job_titles.state import (
    JobsToExcludeInputState,
    JobsToExcludeState,
)


def compile_not_in_job_titles_subgraph() -> CompiledGraph:
    """Compile the not in job titles subgraph."""
    subgraph_builder = StateGraph(
        JobsToExcludeState,
        input=JobsToExcludeInputState,
        output=KeywordsInputState,
    )
    subgraph_builder.add_node(
        "judge_existing_not_in_job_titles", judge_existing_not_in_job_titles
    )
    subgraph_builder.add_node(
        "apply_changes_not_in_job_titles", apply_changes_not_in_job_titles
    )

    subgraph_builder.add_edge(START, "judge_existing_not_in_job_titles")
    subgraph_builder.add_edge(
        "judge_existing_not_in_job_titles", "apply_changes_not_in_job_titles"
    )
    subgraph_builder.add_edge("apply_changes_not_in_job_titles", END)

    not_in_job_titles_subgraph = subgraph_builder.compile()
    not_in_job_titles_subgraph.name = "new_not_in_job_titles_subgraph"
    return not_in_job_titles_subgraph
