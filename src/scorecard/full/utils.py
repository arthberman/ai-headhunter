"""Utility functions used in our graph."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langgraph.pregel import RetryPolicy


def init_model(fully_specified_name: str) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return init_chat_model(model, model_provider=provider, temperature=0)


def get_retry_policy() -> RetryPolicy:
    """Get the retry policy."""
    return RetryPolicy(
        initial_interval=1.0,
        backoff_factor=2.0,
        max_attempts=3,
        jitter=True,
    )
