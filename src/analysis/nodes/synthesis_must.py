from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.full.state import MainGraphState
from analysis.iterative.configuration import Configuration
from utils import init_model


def node_synthesis_must(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Synthesize the must criteria."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = hub.pull("")

    # Initialize the model
    raw_model = init_model(configuration.analysis_model)
    model = raw_model.with_structured_output()

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    return {"scored_location_criterion": "res"}
