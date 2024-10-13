"""Utility functions used in our graph."""

import asyncio
import functools
import logging
from datetime import datetime
from enum import Enum

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langgraph.pregel import RetryPolicy

from scorecard.models.scorecard import (
    ImportanceLevel,
    Scorecard,
    ScoringDistribution,
)


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


def get_retry_policy() -> RetryPolicy:
    """Get the retry policy."""
    return RetryPolicy(
        initial_interval=1.0,
        backoff_factor=2.0,
        max_attempts=3,
        jitter=True,
    )


def prepare_scoring_instructions(
    criterion_id: str, scorecard: Scorecard
) -> tuple[str, ImportanceLevel]:
    """Prepare scoring instructions for a criterion and return the importance level."""
    # Find the criterion in the scorecard
    criterion = None
    importance_level = None
    for level, criteria_list in [
        (ImportanceLevel.MUST_HAVE, scorecard.must_have_criteria),
        (ImportanceLevel.IMPORTANT, scorecard.important_criteria),
        (ImportanceLevel.NICE_TO_HAVE, scorecard.nice_to_have_criteria),
    ]:
        for c in criteria_list:
            if c.id == criterion_id:
                criterion = c
                importance_level = level
                break
        if criterion:
            break

    if not criterion:
        raise ValueError(
            f"Criterion with ID {criterion_id} not found in the scorecard."
        )

    instructions = []

    # Add importance level instruction
    instructions.append(
        f"1. Consider the importance level of the criterion: {importance_level.value}"
    )

    if importance_level == ImportanceLevel.MUST_HAVE:
        instructions.append(
            "   - This criterion is essential. A score below 0.6 should disqualify the candidate."
        )
    elif importance_level == ImportanceLevel.IMPORTANT:
        instructions.append(
            "   - This criterion carries significant weight but is not necessarily disqualifying if not fully met."
        )
    elif importance_level == ImportanceLevel.NICE_TO_HAVE:
        instructions.append(
            "   - This criterion is beneficial but not critical for the role."
        )

    # Add scoring distribution instruction
    if criterion.scoring_distribution:
        instructions.append(
            f"2. Apply the {criterion.scoring_distribution.value} scoring distribution:"
        )

        if criterion.scoring_distribution == ScoringDistribution.BINARY:
            instructions.append(
                "   - Score is either 0 (criterion not met) or 1 (criterion met)."
            )
        elif criterion.scoring_distribution == ScoringDistribution.CONTINUOUS:
            instructions.append(
                "   - Score ranges [not met = 0, low met = 0.3, good met = 0.6 and excellent met = 0.9], allowing for partial fulfillment of the criterion."
            )
        elif criterion.scoring_distribution == ScoringDistribution.GAUSSIAN:
            instructions.append(
                "   - This distribution assumes that the majority of people will score in the middle, with a small percentage scoring very high or very low."
            )

    # Add simplified confidence level instruction
    instructions.append("3. Determine your confidence level:")
    instructions.append(
        "   - LOW = 0.2: When you need to make significant inferences or have limited information to support your evaluation."
    )
    instructions.append(
        "   - MEDIUM = 0.5: When you need to make reasonable inferences based on available information, but you're fairly confident in your assessment."
    )
    instructions.append(
        "   - HIGH = 0.8: When the information is directly available and clearly supports your evaluation."
    )

    # Add criterion-specific information
    instructions.append(f"\nCriterion Description: {criterion.description}")
    if criterion.context:
        instructions.append(f"Context: {criterion.context}")
    instructions.append(f"Type: {criterion.type.value}")

    return "\n".join(instructions), importance_level
