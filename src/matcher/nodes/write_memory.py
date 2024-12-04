from langgraph.store.base import BaseStore

from matcher.state import MainGraphState


def node_write_memory(state: MainGraphState, *, store: BaseStore):
    """Save the memory."""
    if state.batch_store_ops:
        store.batch(state.batch_store_ops)

    # Clear the batch store ops with CLEAR command from reducer_list
    return {"batch_store_ops": "CLEAR"}
