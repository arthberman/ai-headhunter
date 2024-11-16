from typing import Union


def reducer_list(existing: list, updates: Union[list, str]) -> list:
    """Reducer for a list with a CLEAR command."""
    if updates == "CLEAR":
        return []
    elif isinstance(updates, list):
        return existing + updates
    return existing
