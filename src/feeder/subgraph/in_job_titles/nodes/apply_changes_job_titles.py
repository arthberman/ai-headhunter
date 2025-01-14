from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda
from trustcall import create_extractor

from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from feeder.subgraph.in_job_titles.state import NewJobTitlesSubgraphState


def apply_changes_job_titles(
    state: NewJobTitlesSubgraphState,
) -> NewJobTitlesSubgraphState:
    """Apply changes to job titles by removing titles mentioned in feedback."""
    if not state.feedback_judge or not state.json_object:
        return state

    current_titles = state.json_object.include
    anomalies = state.feedback_judge.anomalies
    titles_to_remove = {anomaly.title for anomaly in anomalies}

    updated_titles = [
        title for title in current_titles if title not in titles_to_remove
    ]

    state.json_object.include = updated_titles
    return state
