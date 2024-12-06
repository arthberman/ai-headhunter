from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from matcher.configuration import Configuration
from matcher.sub_graph.infer_enrichment.state import (
    MainInferEnrichmentState,
    OutputInferEnrichmentState,
)
from utils import format_data, get_prompt, init_model


class CultureSynthesis(BaseModel):
    """Culture matcher synthesis."""

    synthesis: str = Field(
        description="Synthesis of the matcher of the culture of the candidate. (max 600 characters)"
    )


async def node_infer_culture(
    state: MainInferEnrichmentState, config: RunnableConfig
) -> OutputInferEnrichmentState:
    """Analyze the culture of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.matcher_model)

    # Initialize the prompt (sync function)
    prompt = get_prompt("analysis-candidate-culture")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(CultureSynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        CultureSynthesis,
        await chain.ainvoke(
            {
                "candidate": format_data(state.profile),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
            }
        ),
    )

    return {"inferred_culture": res.synthesis}
