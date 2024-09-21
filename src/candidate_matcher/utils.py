"""Utility functions used in our graph."""

from datetime import datetime
from enum import Enum
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableConfig

from candidate_matcher.configuration import Configuration


def init_model(fully_specified_name: str) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return init_chat_model(model, model_provider=provider, temperature=0)


def format_data(data):
    """Format data for output."""
    if isinstance(data, dict):
        return {k: format_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [format_data(item) for item in data]
    elif isinstance(data, datetime):
        return data.strftime("%Y-%m-%d")
    elif isinstance(data, Enum):
        return data.value
    elif hasattr(data, "__dict__"):
        return format_data(data.__dict__)
    else:
        return data
