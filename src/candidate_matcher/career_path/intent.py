from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig

from candidate_matcher.career_path.models import CareerPathOutput
from candidate_matcher.configuration import Configuration
from candidate_matcher.state import MainGraphState
from candidate_matcher.utils import init_model


def node_career_path_intent(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Enrich the profile with language proficiency."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.career_path_model)

    # Initialize the prompt
    prompt = hub.pull("analyze-career-path-intent")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(CareerPathOutput)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        CareerPathOutput,
        chain.invoke(
            {
                "candidate_experiences": state.profile.experiences,
                "job_synthesis": state.job_synthesis,
            }
        ),
    )

    return {"career_path_intent": res}
