from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from src.feeder.subgraph.in_job_titles.nodes.apply_changes_job_titles import (
    apply_changes_job_titles,
)
from src.feeder.subgraph.in_job_titles.nodes.judge_existing_job_title import (
    judge_existing_job_title,
)
from src.feeder.subgraph.in_job_titles.state import (
    NewJobTitlesSubgraphInputState,
    NewJobTitlesSubgraphOutputState,
    NewJobTitlesSubgraphState,
)
from src.feeder.utils.retry_policy import get_retry_policy


def compile_new_job_titles_subgraph() -> CompiledGraph:
    """Compile new job titles subgraph.

    Processing Flow:
    1. judge_existing_job_title: LLM judges existing job titles
    2. apply_changes_job_titles: apply the changes from the feedback judge to clean the new job titles list

    Retry Policy:
    - Applied to LLM operations (judge_existing_job_title)
    - Not needed for deterministic changes
    """
    subgraph_builder = StateGraph(
        NewJobTitlesSubgraphState,
        input=NewJobTitlesSubgraphInputState,
        output=NewJobTitlesSubgraphOutputState,
    )
    # add nodes
    subgraph_builder.add_node(
        "judge_existing_job_title",
        judge_existing_job_title,
        retry=get_retry_policy(),
    )
    subgraph_builder.add_node("apply_changes_job_titles", apply_changes_job_titles)
    # add edges
    subgraph_builder.add_edge(START, "judge_existing_job_title")
    subgraph_builder.add_edge("judge_existing_job_title", "apply_changes_job_titles")
    subgraph_builder.add_edge("apply_changes_job_titles", END)

    new_job_titles_subgraph = subgraph_builder.compile()
    new_job_titles_subgraph.name = "new_job_titles_subgraph"
    return new_job_titles_subgraph
