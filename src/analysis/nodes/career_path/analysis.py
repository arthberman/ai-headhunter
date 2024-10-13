from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig

from analysis.iterative.configuration import Configuration
from analysis.iterative.state import MainGraphState
from analysis.iterative.utils import init_model, log_cancelled_error
from analysis.nodes.career_path.models import CareerPathOutput


@log_cancelled_error
def node_career_path(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Analyze the career path of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.career_path_model)

    # Initialize the prompt
    prompt = hub.pull("analyze-career-path")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(CareerPathOutput)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        CareerPathOutput,
        chain.invoke(
            {
                "profile": state.profile.model_dump() if state.profile else None,
                "job_synthesis": state.job_synthesis,
            }
        ),
    )

    return {"career_path": res}
