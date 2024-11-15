from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.configuration import Configuration
from analysis.models.synthesis import Synthesis
from analysis.state import MainGraphState
from utils import format_data, get_extended_scored_criterion, get_prompt, init_model


def node_conclude(state: MainGraphState, config: RunnableConfig) -> MainGraphState:
    """Conclude the overall analysis."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("generate-analysis-synthesis")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(Synthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Extend the scored criterion with the scorecard
    extended_scored_criterion = get_extended_scored_criterion(
        state.scored_criterion, state.scorecard
    )

    # Invoke the chain
    res = cast(
        Synthesis,
        chain.invoke(
            {
                "profile": format_data(state.profile),
                "extended_scored_criterion": extended_scored_criterion,
                "job_synthesis": state.job_synthesis,
                "output_schema": Synthesis.model_json_schema(),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%Y-%m-%d (Y-m-d)"),
            }
        ),
    )

    return {"synthesis_overall": res}
