from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig

from analysis.full.configuration import Configuration
from analysis.full.state import MainGraphState
from analysis.models.profile import ProfileAge
from utils import format_data, init_model


def node_estimate_profile_age(
    state: MainGraphState,
    *,
    config: Optional[RunnableConfig] = None,
) -> MainGraphState:
    """Estimate the age of the profile."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Initialize the prompt
    prompt = hub.pull("analysis-find-age:development")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(ProfileAge)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    res = cast(
        ProfileAge,
        chain.invoke(
            {
                "profile": format_data(state.profile),
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    updated_profile = state.profile.model_copy(update={"age_range": res})

    return {"profile": updated_profile}
