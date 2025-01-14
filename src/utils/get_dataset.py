from functools import lru_cache
from typing import Any, List

from langsmith import Client


@lru_cache(maxsize=32)  # Cache up to 32 most recent datasets
def get_dataset(dataset_name: str) -> List[Any]:
    """Get a dataset from LangSmith with caching."""
    try:
        # Initialize LangSmith client
        ls_client = Client()

        # Fetch examples from LangSmith
        examples = list(ls_client.list_examples(dataset_name=dataset_name))
        return examples

    except Exception as e:
        raise Exception(f"Error fetching dataset from LangSmith: {str(e)}")
