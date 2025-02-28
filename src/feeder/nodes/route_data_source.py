from typing import Literal

from langgraph.types import Command

from src.feeder.state import OverallState


def route_data_source(
    state: OverallState,
) -> Command[
    Literal[
        "create_queries",
        "create_linkedin_recruiter_queries",
    ]
]:
    """Route the data source based on the state."""
    if state.data_source == "crustdata":
        return Command(
            goto="create_queries",
        )
    else:
        return Command(
            goto="create_linkedin_recruiter_queries",
        )
