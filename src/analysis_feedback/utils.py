"""Utility functions used in our graph."""

import asyncio
import functools
import logging
from datetime import datetime
from enum import Enum

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


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


def log_cancelled_error(func):
    """Log the error when a function is cancelled."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except asyncio.exceptions.CancelledError as e:
            logging.error(f"Function {func.__name__} was cancelled: {e}")
            logging.error(f"Cancellation context: {e.__context__}")
            logging.error(f"Cancellation cause: {e.__cause__}")
            logging.error("Traceback: ", exc_info=True)
            raise  # Re-raise the exception after logging

    return wrapper
