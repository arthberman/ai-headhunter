from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.configuration import Configuration
from analysis.models.synthesis import IntentSynthesis
from analysis.state import MainGraphState
from utils import format_data, get_prompt, init_model


def node_synthetize_intent(
    state: MainGraphState, config: RunnableConfig
) -> MainGraphState:
    """Synthesize the intent of the profile."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-intent")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(IntentSynthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Invoke the chain
    res = cast(
        IntentSynthesis,
        chain.invoke(
            {
                "profile": format_data(state.profile),
                "synthesis_hierarchy": state.synthesis_hierarchy,
                "synthesis_open_to_work": state.synthesis_open_to_work,
                "system_time": datetime.now().strftime("%Y-%m-%d (Y-m-d)"),
                "output_language": configuration.output_language,
            }
        ),
    )

    return {"synthesis_intent": res}
