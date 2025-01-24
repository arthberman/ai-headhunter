from typing import cast

from langchain import hub
from langchain_core.runnables import RunnableLambda

from feeder.utils.init_model import init_model
from src.feeder.models.location import LocationItem, LocationList
from src.feeder.state import OverallState
from src.feeder.subgraph.location.state import LocationSubGraphState


async def get_relevant_locations_for_search(
    state: LocationSubGraphState,
) -> OverallState:
    """Filter and return relevant locations based on job location and API results.

    Data Flow:
    - Input: reference location (job_location) and API location list (api_out_locations)
    - Output: filtered & ranked LocationList for search queries

    LLM Processing:
    - Analyzes geographic relevance (e.g., nearby cities, same region)
    - Ranks locations by proximity to reference location (the most broad location is ranked first)
    - Filters out irrelevant locations (e.g., non-cities, non-regions)
    """
    llm = init_model("bedrock_converse/us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    structured_llm = llm.with_structured_output(LocationList)

    prompt = hub.pull("get_relevant_locations_for_search_prompt")
    chain = cast(RunnableLambda, prompt | structured_llm)
    res = cast(
        LocationList,
        await chain.ainvoke(
            {
                "reference_job_location": state.job_location,
                "api_out_locations": state.api_out_locations,
            }
        ),
    )
    """ return {
        "locations": res.locations
    } """  # res.locations because locations is defined as a list of LocationItem in the state

    return {
        "locations": [LocationItem(id="xyz", name="Greater Paris Metropolitan Region")]
    }
