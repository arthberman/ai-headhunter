"""Define the configurable parameters for the memory service."""

from typing import Any, Literal

from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from memory_graph.models import Company


class MemoryConfig(BaseModel):
    """Configuration for memory-related operations."""

    name: str = Field(
        description="This tells the model how to reference the function and organizes related memories within the namespace."
    )
    description: str = Field(
        description="Description for what this memory type is intended to capture."
    )
    parameters: dict[str, Any] = Field(
        description="The JSON Schema of the memory document to manage."
    )
    system_prompt: str = Field(
        default="You are a Human Resources recruiter.",
        description="The system prompt to use for the memory assistant.",
    )
    update_mode: Literal["patch", "insert"] = Field(
        default="patch",
        description="Whether to continuously patch the memory, or treat each new generation as a new memory.",
    )


class Configuration(BaseModel):
    """Main configuration class for the memory graph system."""

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = Field(
        default="openai/gpt-4o-mini",
        description="The name of the language model to use for the agent. Should be in the form: provider/model-name.",
    )
    memory_types: list[MemoryConfig] = Field(
        default_factory=lambda: DEFAULT_MEMORY_CONFIGS.copy(),
        description="The memory_types for the memory assistant.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: RunnableConfig | None = None
    ) -> "Configuration":
        """Load configuration w/ defaults for the given invocation."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        return cls(**configurable)


DEFAULT_MEMORY_CONFIGS = [
    MemoryConfig(
        name="Company",
        description="Update this document to maintain up-to-date information about a company.",
        update_mode="patch",
        parameters=Company.model_json_schema(),
    ),
]
