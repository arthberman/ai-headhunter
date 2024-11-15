from datetime import datetime
from typing import List, Optional, cast

from utils import get_prompt
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from analysis.configuration import Configuration
from analysis.models.language import LanguageProficiency
from analysis.sub_graph.infer_enrichment.state import (
    MainInferEnrichmentState,
    OutputInferEnrichmentState,
)
from utils import format_data, init_model


class LanguageProficiency(BaseModel):
    """Language proficiency."""

    languages: List[LanguageProficiency] = Field(
        description="List of language proficiencies, each containing a language and its corresponding level"
    )


def node_infer_languages(
    state: MainInferEnrichmentState, config: RunnableConfig
) -> OutputInferEnrichmentState:
    """Analyze the language proficiency of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = get_prompt("analysis-candidate-language")

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
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%Y-%m-%d (Y-m-d)"),
            }
        ),
    )

    return {"inferred_languages": res.languages}
