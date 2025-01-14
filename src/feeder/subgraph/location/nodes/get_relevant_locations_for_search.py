from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from feeder.models.location import LocationList
from feeder.state import OverallState
from feeder.subgraph.location.state import LocationSubGraphState


def get_relevant_locations_for_search(
    state: LocationSubGraphState,
) -> OverallState:
    """Filter and return relevant locations based on job location and API results."""
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(LocationList)

    prompt = hub.pull("get_relevant_locations_for_search_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        LocationList,
        chain.invoke(
            {
                "reference_job_location": state.job_location,
                "api_out_locations": state.api_out_locations,
            }
        ),
    )
    return {"locations": res}
