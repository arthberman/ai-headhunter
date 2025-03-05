from feeder.subgraph.reprocess_raw_query.state import ReprocessRawQueryState


def combine_raw_query(state: ReprocessRawQueryState):
    """Combine raw query into one."""
    json_object = state.json_object

    return {"json_object": json_object}
