from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from analysis.full.configuration import Configuration
from analysis.sub_graph.infer_enrichment.state import (
    MainInferEnrichmentState,
    OutputInferEnrichmentState,
)
from utils import format_data, init_model


class SectorSynthesis(BaseModel):
    """Sector analysis synthesis."""

    synthesis: str = Field(
        description="Synthesis of the analysis of the sector of the candidate. (max 600 characters)"
    )


def node_infer_sector(
    state: MainInferEnrichmentState, config: Optional[RunnableConfig] = None
) -> OutputInferEnrichmentState:
    """Analyze the sector of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = hub.pull("analysis-candidate-sector")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(SectorSynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        SectorSynthesis,
        chain.invoke(
            {
                "candidate": format_data(state.profile),
                "output_schema": SectorSynthesis.model_json_schema(),
                "output_language": "en",
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    return {"infer_sector": res.synthesis}
