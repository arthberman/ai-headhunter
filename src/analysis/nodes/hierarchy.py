from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import Runnable, RunnableConfig

from analysis.full.configuration import Configuration
from analysis.full.state import MainGraphState
from analysis.models.synthesis import HierarchySynthesis
from utils import get_candidate_timeline, init_model


def node_hierarchy(state: MainGraphState, config: Optional[RunnableConfig] = None):
    """Analyze the language proficiency of the candidate."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the raw model with the provided configuration
    raw_model = init_model(configuration.analysis_model)

    # Initialize the prompt
    prompt = hub.pull("candidate-analysis-hierarchy:production")

    # Bind the model to the structured output
    model = raw_model.with_structured_output(HierarchySynthesis)

    # Create the chain
    chain = cast(Runnable, prompt | model)

    # Invoke the chain
    res = cast(
        HierarchySynthesis,
        chain.invoke(
            {
                "candidate_timeline": get_candidate_timeline(
                    state.profile, with_detail=True
                ),
                "target_role": state.job_synthesis,
                "output_language": configuration.output_language,
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    return {"synthesis_hierarchy": res}
