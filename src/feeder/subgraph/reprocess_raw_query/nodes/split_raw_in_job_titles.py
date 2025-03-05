from typing import Literal

from langgraph.types import Command

from feeder.subgraph.reprocess_raw_query.state import ReprocessRawQueryInputState


def split_raw_in_job_titles(
    state: ReprocessRawQueryInputState,
) -> Command[Literal["combine_raw_query"]]:
    """Separate raw_in_job_titles from json_object."""
    raw_in_job_titles = state.json_object.in_job_titles

    return Command(
        update={"in_job_titles": raw_in_job_titles}, goto="combine_raw_query"
    )
