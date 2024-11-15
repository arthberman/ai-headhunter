from langgraph.store.base import BaseStore
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def safe_store_put(store: BaseStore, namespace: tuple, key: str, value: any) -> None:
    """Store value with retry mechanism."""
    store.put(namespace, key, value)
