from feeder.subgraph.reprocess_raw_query.state import ReprocessRawQueryInputState


def split_raw_not_in_job_titles(
    state: ReprocessRawQueryInputState,
):
    """Separate raw_in_job_titles from json_object."""
    raw_not_in_job_titles = state.json_object.not_in_job_titles

    return {"not_in_job_titles": raw_not_in_job_titles}
