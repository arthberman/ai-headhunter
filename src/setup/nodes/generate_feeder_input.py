from typing import cast

from langchain_core.runnables import RunnableConfig
from langgraph.types import StreamWriter

from feeder.models.job_offer import JobOfferDescription
from setup.configuration import Configuration
from setup.state import ScorecardGraphState
from utils import get_prompt, init_model


def node_generate_feeder_input(
    state: ScorecardGraphState, writer: StreamWriter, *, config: RunnableConfig
) -> ScorecardGraphState:
    """Generate the input for the feeder subgraph."""
    # Load configuration from the provided RunnableConfig
    configuration = Configuration.from_runnable_config(config)

    prompt = get_prompt("generate-feeder-input")
    raw_model = init_model(configuration.structure_model)
    model = raw_model.with_structured_output(JobOfferDescription)

    chain = prompt | model

    res = cast(
        JobOfferDescription,
        chain.invoke(
            {
                "scorecard": state.scorecard.model_dump(mode="json"),
                "resources": [
                    resource.model_dump(mode="json") for resource in state.resources
                ],
                "questions": state.get_formatted_questions(),
            }
        ),
    )

    return {"feeder_input": res}
