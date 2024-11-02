from datetime import datetime
from typing import List, Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from analysis.full.configuration import Configuration
from analysis.full.state import MainGraphState
from analysis.models.language import LanguageProficiency
from utils import format_data, init_model


class LanguageProficiency(BaseModel):
    """Language proficiency."""

    languages: List[LanguageProficiency] = Field(
        description="List of language proficiencies, each containing a language and its corresponding level"
    )


def node_language_enrichment(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Enrich the profile with language proficiency."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = hub.pull("generate-language-enrichment:production")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(LanguageProficiency)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        LanguageProficiency,
        chain.invoke(
            {
                "profile": format_data(state.profile),
                "output_schema": LanguageProficiency.model_json_schema(),
                "output_language": "en",
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    return {"language_enrichment": res.languages}
