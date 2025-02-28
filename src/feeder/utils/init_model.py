from typing import Optional

from botocore.config import Config
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.rate_limiters import BaseRateLimiter

load_dotenv()


def init_model(
    fully_specified_name: str,
    *,
    temperature: float | None = 0.0,
    rate_limiter: Optional[BaseRateLimiter] = None,
) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name

    kwargs = {
        "model": model,
        "model_provider": provider,
        "rate_limiter": rate_limiter,
    }

    if temperature is not None:
        kwargs["temperature"] = temperature

    if model == "o3-mini":
        kwargs["temperature"] = None
        kwargs["reasoning_effort"] = "high"

    if provider == "bedrock" or provider == "bedrock_converse":
        config = Config(read_timeout=120)
        return init_chat_model(
            model, model_provider=provider, temperature=temperature, config=config
        )

    return init_chat_model(**kwargs)
