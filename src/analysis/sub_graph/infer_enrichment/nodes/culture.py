from datetime import datetime
from typing import Optional, cast

from utils import get_prompt
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from analysis.full.configuration import Configuration
from analysis.sub_graph.infer_enrichment.state import (
    MainInferEnrichmentState,
    OutputInferEnrichmentState,
)
from utils import format_data, init_model


class CultureSynthesis(BaseModel):
    """Culture analysis synthesis."""

    synthesis: str = Field(
        description="Synthesis of the analysis of the culture of the candidate. (max 600 characters)"
    )


def node_infer_culture(
    state: MainInferEnrichmentState, config: Optional[RunnableConfig] = None
) -> OutputInferEnrichmentState:
    """Analyze the culture of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = get_prompt("analysis-candidate-culture")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(CultureSynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        CultureSynthesis,
        chain.invoke(
            {
                "candidate": format_data(state.profile),
                "output_schema": CultureSynthesis.model_json_schema(),
                "output_language": configuration.output_language,
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    return {"inferred_culture": res.synthesis}
