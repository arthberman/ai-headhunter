from feeder.subgraph.reprocess_raw_query.state import ReprocessRawQueryInputState


def split_raw_in_job_titles(
    state: ReprocessRawQueryInputState,
):
    """Separate raw_in_job_titles from json_object."""
    raw_in_job_titles = state.json_object.in_job_titles

    return {"in_job_titles": raw_in_job_titles}
