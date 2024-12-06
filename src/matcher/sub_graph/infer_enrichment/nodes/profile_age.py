from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig

from matcher.configuration import Configuration
from matcher.models.profile import ProfileAge
from matcher.sub_graph.infer_enrichment.state import MainInferEnrichmentState
from utils import format_data, get_prompt, init_model


async def node_infer_age(
    state: MainInferEnrichmentState,
    *,
    config: RunnableConfig,
) -> MainInferEnrichmentState:
    """Estimate the age of the profile."""
    # Skip if already processed
    if state.profile.age_range:
        return {"profile": state.profile}

    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.default_model)

    # Initialize the prompt (sync function)
    prompt = get_prompt("analysis-find-age")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(ProfileAge)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    res = cast(
        ProfileAge,
        await chain.ainvoke(
            {
                "profile": format_data(state.profile),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
            }
        ),
    )

    updated_profile = state.profile.model_copy(update={"age_range": res})

    return {"profile": updated_profile}
