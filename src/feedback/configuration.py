from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """The configuration for the feedback."""

    default_model: str = Field(
        default="bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the matcher. "
        "Should be in the form: provider/model-name.",
    )

    thinking_model: str = Field(
        default="fireworks/accounts/fireworks/models/deepseek-r1",
        description="The name of the language model to use for the thinking. "
        "Should be in the form: provider/model-name.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: RunnableConfig | None = None
    ) -> "Configuration":
        """Load configuration w/ defaults for the given invocation."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        return cls(**configurable)
