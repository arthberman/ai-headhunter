from typing import Literal

from langgraph.types import Command

from feeder.subgraph.reprocess_raw_query.state import ReprocessRawQueryInputState


def split_raw_keywords(
    state: ReprocessRawQueryInputState,
) -> Command[Literal["combine_raw_query"]]:
    """Separate raw keywords from json_object."""
    raw_keywords = state.json_object.keywords

    return Command(
        update={"keywords": raw_keywords},
        goto="combine_raw_query",
    )
