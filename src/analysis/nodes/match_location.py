from datetime import datetime
from typing import Optional, cast

from langchain import hub
from langchain_core.runnables import RunnableConfig, RunnableLambda

from analysis.full.state import MainGraphState
from analysis.iterative.configuration import Configuration
from analysis.models.synthesis import LocationSynthesis
from scorecard.models.scorecard import CriterionType
from utils import init_model
from utils.candidate_timeline import get_candidate_timeline


def node_synthesis_location(
    state: MainGraphState, config: Optional[RunnableConfig] = None
) -> MainGraphState:
    """Analyze the candidate's location."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    # Initialize the prompt
    prompt = hub.pull("candidate-analysis-location")

    # Initialize the model
    raw_model = init_model(configuration.analysis_model)
    model = raw_model.with_structured_output(LocationSynthesis)

    # Create the chain
    chain = cast(RunnableLambda, prompt | model)

    # Get scorecard criteria of type location
    location_criteria = [
        criterion
        for criterion in state.scorecard.criteria
        if criterion.type == CriterionType.LOCATION
    ]

    # Invoke the chain
    res = cast(
        LocationSynthesis,
        chain.invoke(
            {
                "job_location_criteria": location_criteria,
                "candidate_timeline": get_candidate_timeline(state.profile),
                "candidate_headline_location": f"{state.profile.city}, {state.profile.state}, {state.profile.country}",
                "output_language": "en",
                "system_time": datetime.now().isoformat(),
            }
        ),
    )

    return {"synthesis_location": res}
