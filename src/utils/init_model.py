from typing import Optional

from botocore.config import Config
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.rate_limiters import BaseRateLimiter


def init_model(
    fully_specified_name: str, rate_limiter: Optional[BaseRateLimiter] = None
) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name

    if provider == "bedrock" or provider == "bedrock_converse":
        config = Config(read_timeout=120)
        return init_chat_model(
            model,
            model_provider=provider,
            temperature=0,
            config=config,
            rate_limiter=rate_limiter,
        )

    return init_chat_model(
        model, model_provider=provider, temperature=0, rate_limiter=rate_limiter
    )
