from langgraph.graph import END, START, StateGraph
from langgraph.graph.graph import CompiledGraph

from src.feeder.subgraph.process_keywords.state import KeywordsInputState
from src.feeder.subgraph.process_not_in_job_titles.nodes.apply_changes_not_in_job_titles import (
    apply_changes_not_in_job_titles,
)
from src.feeder.subgraph.process_not_in_job_titles.nodes.judge_existing_not_in_job_titles import (
    judge_existing_not_in_job_titles,
)
from src.feeder.subgraph.process_not_in_job_titles.state import (
    JobsToExcludeInputState,
    JobsToExcludeState,
)
from src.feeder.utils.retry_policy import get_retry_policy


def compile_not_in_job_titles_subgraph() -> CompiledGraph:
    """Compile not in job titles subgraph.

    Processing flow:
    1. judge_existing_not_in_job_titles: LLM judges existing job titles
    2. apply_changes_not_in_job_titles: apply the changes from the feedback judge to clean the new job titles list

    Retry Policy:
    - Applied to LLM operations (judge_existing_not_in_job_titles)
    - Not needed for deterministic changes
    """
    subgraph_builder = StateGraph(
        JobsToExcludeState,
        input=JobsToExcludeInputState,
        output=KeywordsInputState,
    )
    # add nodes
    subgraph_builder.add_node(
        "judge_existing_not_in_job_titles",
        judge_existing_not_in_job_titles,
        retry=get_retry_policy(),
    )
    subgraph_builder.add_node(
        "apply_changes_not_in_job_titles", apply_changes_not_in_job_titles
    )
    # add edges
    subgraph_builder.add_edge(START, "judge_existing_not_in_job_titles")
    subgraph_builder.add_edge(
        "judge_existing_not_in_job_titles", "apply_changes_not_in_job_titles"
    )
    subgraph_builder.add_edge("apply_changes_not_in_job_titles", END)

    not_in_job_titles_subgraph = subgraph_builder.compile()
    not_in_job_titles_subgraph.name = "new_not_in_job_titles_subgraph"
    return not_in_job_titles_subgraph
