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

    # Compute score based on hierarchy and open_to_work synthesis results
    scores = [
        state.synthesis_hierarchy.score.value,
        state.synthesis_open_to_work.score.value,
    ]
    heuristic_score = (
        "FAIL" if "FAIL" in scores else "DOUBT" if "DOUBT" in scores else "SUCCESS"
    )

    # Invoke the chain
    res = cast(
        IntentSynthesis,
        chain.invoke(
            {
                "profile": format_data(state.profile),
                "synthesis_hierarchy": format_data(state.synthesis_hierarchy),
                "synthesis_open_to_work": format_data(state.synthesis_open_to_work),
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
                "output_language": configuration.output_language,
                "score": heuristic_score,
            }
        ),
    )

    return {"synthesis_intent": res}
