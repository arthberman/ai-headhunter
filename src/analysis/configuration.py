"""Define the configurable parameters for the matcher."""

from langchain_core.runnables import RunnableConfig, ensure_config
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """The configuration for the matcher."""

    default_model: str = Field(
        default="bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the analysis. "
        "Should be in the form: provider/model-name.",
    )

    analysis_model: str = Field(
        default="bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the analysis. "
        "Should be in the form: provider/model-name.",
    )

    enrichment_model: str = Field(
        default="openai/gpt-4o-mini",
        description="The name of the language model to use for the enrichment. "
        "Should be in the form: provider/model-name.",
    )

    synthesis_model: str = Field(
        default="bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        description="The name of the language model to use for the synthesis. "
        "Should be in the form: provider/model-name.",
    )

    max_search_results: int = Field(
        default=5,
        description="The maximum number of search results to return for each search query.",
    )

    analysis_max_loops: int = Field(
        default=3,
        description="The maximum number of iterations to run the analysis for.",
    )

    output_language: str = Field(
        default="English",
        description="The language to use for the LLM output.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: RunnableConfig | None = None
    ) -> "Configuration":
        """Load configuration w/ defaults for the given invocation."""
        config = ensure_config(config)
        configurable = config.get("configurable") or {}
        return cls(**configurable)
