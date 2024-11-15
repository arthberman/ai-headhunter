"""Handle patch-based memory updates. Hot path implementation."""

from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import PutOp
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from trustcall import create_extractor

from analysis.configuration import Configuration
from utils import get_prompt, init_model


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
)
def handle_patch_memory(
    namespace: tuple,
    key: str,
    information: str,
    existing_item: dict | None,
    prompt: str,
    schema_model: Type[BaseModel],
    *,
    config: RunnableConfig,
) -> PutOp:
    """Extract and update patch-based memories."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Fetch existing memories from the store for this (patch) memory schema
    existing = {schema_model.__name__: existing_item.value} if existing_item else None

    # Create the extractor with the specified memory schema
    extractor = create_extractor(
        init_model(configuration.enrichment_model),
        tools=[schema_model],
        tool_choice=schema_model.__name__,
    )

    # Prepare the messages
    prompt = get_prompt(prompt)
    chat_prompt = ChatPromptTemplate.from_messages(prompt.messages)

    formatted_messages = chat_prompt.format_messages(information=information)

    # Extract and update the patch memory
    result = extractor.invoke(
        {"messages": formatted_messages, "existing": existing}, config
    )
    extracted = result["responses"][0].model_dump(mode="json")

    return PutOp(namespace, key, extracted)
