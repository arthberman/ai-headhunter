from datetime import datetime
from typing import cast

from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.configuration import Configuration
from analysis.models.synthesis import SynthesisOverall
from analysis.state import MainGraphState
from utils import (
    format_data,
    format_scored_criteria,
    get_extended_scored_criterion,
    get_prompt,
    init_model,
)


def node_conclude(state: MainGraphState, config: RunnableConfig) -> MainGraphState:
    """Conclude the overall analysis."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = get_prompt("analysis-conclusion")

    # Initialize the model
    raw_model = init_model(configuration.synthesis_model)
    model = raw_model.with_structured_output(SynthesisOverall)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Extend the scored criterion with the scorecard
    extended_scored_criterion = get_extended_scored_criterion(
        state.scored_criterion, state.scorecard
    )

    # Invoke the chain
    res = cast(
        SynthesisOverall,
        chain.invoke(
            {
                "extended_scored_criterion": format_scored_criteria(
                    extended_scored_criterion,
                    state.scored_criterion,
                    state.scorecard,
                ),
                "job_synthesis": format_data(state.job_synthesis),
                "synthesis_hierarchy": format_data(state.synthesis_hierarchy),
                "synthesis_open_to_work": format_data(state.synthesis_open_to_work),
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%Y-%m-%d (Y-m-d)"),
            }
        ),
    )

    return {"synthesis_overall": res}
