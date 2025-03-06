from feeder.subgraph.reprocess_raw_query.state import ReprocessRawQueryInputState


def split_raw_keywords(
    state: ReprocessRawQueryInputState,
):
    """Separate raw keywords from json_object."""
    raw_keywords = state.json_object.keywords

    return {"keywords": raw_keywords}
