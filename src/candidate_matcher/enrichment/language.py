from typing import List, Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from candidate_matcher.configuration import Configuration
from candidate_matcher.models.language import LanguageProficiency
from candidate_matcher.state import MainGraphState
from candidate_matcher.utils import init_model, log_cancelled_error


class StructuredOutput(BaseModel):
    """Structured output for the language enrichment model."""

    language_proficiency: List[LanguageProficiency] = Field(
        description="List of language proficiencies, each containing a language and its corresponding level"
    )


@log_cancelled_error
def node_language_enrichment(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Enrich the profile with language proficiency."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = hub.pull("generate-language-enrichment")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(StructuredOutput)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        StructuredOutput,
        chain.invoke({"profile": state.profile, "knowledge_points": ""}),
    )

    return {"language_enrichment": res.language_proficiency}
