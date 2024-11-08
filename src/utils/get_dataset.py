from typing import Any, Dict, List

from langsmith import Client

# Cache dictionary to store datasets
_dataset_cache: Dict[str, List[Any]] = {}


def get_dataset(dataset_name: str) -> List[Any]:
    """Get a dataset from LangSmith with caching."""
    # Check if dataset is already in cache
    if dataset_name in _dataset_cache:
        return _dataset_cache[dataset_name]

    try:
        # Initialize LangSmith client
        ls_client = Client()

        # Fetch examples from LangSmith
        examples = list(ls_client.list_examples(dataset_name=dataset_name))

        # Store in cache
        _dataset_cache[dataset_name] = examples

        return examples

    except Exception as e:
        raise Exception(f"Error fetching dataset from LangSmith: {str(e)}")
