from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field

from analysis.full.configuration import Configuration
from analysis.full.state import MainGraphState
from utils import format_data, init_model


class StructuredOutput(BaseModel):
    """Structured output for the culture analysis model."""

    synthesis: str = Field(
        description="Synthesis of the analysis of the culture of the candidate. (max 600 characters)"
    )


def node_analysis_culture(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Analyze the culture of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = hub.pull("analysis-candidate-culture:production")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(StructuredOutput)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        StructuredOutput,
        chain.invoke({"candidate": format_data(state.profile)}),
    )

    return {"culture_analysis": res.synthesis}
