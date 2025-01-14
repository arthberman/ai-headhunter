from typing import cast

from trustcall import create_extractor

from feeder.models.raw_query import RawQuery
from feeder.utils.init_model import init_model
from feeder.subgraph.not_in_job_titles.state import (
    JobsToExcludeState,
)


def apply_changes_not_in_job_titles(
    state: JobsToExcludeState,
) -> JobsToExcludeState:
    """Apply changes to the list of job titles to exclude based on the feedback of the judge above."""
    if not state.feedback_judge or not state.json_object:
        return state
    current_titles = state.json_object.exclude
    anomalies = state.feedback_judge.anomalies
    titles_to_remove = {anomaly.title for anomaly in anomalies}
    updated_titles = [
        title for title in current_titles if title not in titles_to_remove
    ]
    state.json_object.exclude = updated_titles
    return state
