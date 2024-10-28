"""Define the configurable parameters for the analysis feedback."""

from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """The configuration for the analysis feedback."""

    reformulation_model: str = Field(
        default="bedrock_converse/anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the reformulation. "
        "Should be in the form: provider/model-name.",
    )

    extraction_model: str = Field(
        default="bedrock_converse/anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the extraction. "
        "Should be in the form: provider/model-name.",
    )

    synthesis_model: str = Field(
        default="bedrock_converse/anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the synthesis. "
        "Should be in the form: provider/model-name.",
    )

    analysis_max_loops: int = Field(
        default=5,
        description="The maximum number of loops to run the analysis for.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: RunnableConfig | None = None
    ) -> "Configuration":
        """Load configuration w/ defaults for the given invocation."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        return cls(**configurable)
