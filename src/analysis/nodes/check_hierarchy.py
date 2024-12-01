from datetime import datetime
from typing import cast

from langchain_core.runnables import Runnable, RunnableConfig

from analysis.configuration import Configuration
from analysis.models.synthesis import HierarchySynthesis
from analysis.state import MainGraphState
from utils import format_data, get_candidate_timeline, get_prompt, init_model


def node_check_hierarchy(state: MainGraphState, config: RunnableConfig):
    """Analyze the language proficiency of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = get_prompt("candidate-analysis-hierarchy")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(HierarchySynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        HierarchySynthesis,
        chain.invoke(
            {
                "candidate_timeline": format_data(
                    get_candidate_timeline(state.profile, with_detail=True)
                ),
                "target_role": state.job_synthesis,
                "output_language": configuration.output_language,
                "system_time": datetime.now().strftime("%d %B %Y (%d-%m-%Y)"),
            }
        ),
    )

    return {"synthesis_hierarchy": res}
