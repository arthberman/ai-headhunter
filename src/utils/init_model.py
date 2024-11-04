from botocore.config import Config
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel


def init_model(fully_specified_name: str) -> BaseChatModel:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name

    if provider == "bedrock" or provider == "bedrock_converse":
        config = Config(read_timeout=120)
        return init_chat_model(
            model, model_provider=provider, temperature=0, config=config
        )

    return init_chat_model(model, model_provider=provider, temperature=0)
